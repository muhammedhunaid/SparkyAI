from utils.common_imports import *
from agents.data_agent import DataModel

class DataPreprocessor:
    def __init__(self, app_config, genai,
                 chunk_size: int = 1024, 
                 chunk_overlap: int = 200, 
                 max_processing_attempts: int = 3,
                 enable_async_processing: bool = True,
                 enable_caching: bool = True,
                 logger=False):
        """Initialize DataPreprocessor with enhanced processing capabilities."""
        self.max_processing_attempts = max_processing_attempts
        self.enable_async_processing = enable_async_processing
        self.enable_caching = enable_caching
        self.doc_title = None
        self.doc_category = None
        self.asu_data_agent = DataModel(app_config, genai, logger)
        
        # Enhanced caching system
        self.cache = {} if enable_caching else None
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.cache_timestamps = {}
        
        # Processing statistics
        self.processing_stats = {
            'documents_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time': 0,
            'total_processing_time': 0,
            'failed_documents': 0
        }
        
        # Initialize NLP components
        nltk.download('punkt_tab', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Enhanced regex patterns
        self.WHITESPACE_PATTERN = re.compile(r'\s+')
        self.LINK_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.SPECIAL_CHAR_PATTERN = re.compile(r'[^a-zA-Z0-9\s.,!?;:()\-"\'$]')
        self.EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.PHONE_PATTERN = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        
        self.logger = logger
        self.logger.info(f"@data_processor.py Enhanced DataPreprocessor initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        stats = self.processing_stats.copy()
        if stats['documents_processed'] > 0:
            stats['average_processing_time'] = stats['total_processing_time'] / stats['documents_processed']
            stats['cache_hit_rate'] = stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses']) if (stats['cache_hits'] + stats['cache_misses']) > 0 else 0
        return stats
        
    def clear_cache(self):
        """Clear the processing cache"""
        if self.cache is not None:
            self.cache.clear()
            self.cache_timestamps.clear()
            self.logger.info("@data_processor.py Processing cache cleared")
            
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if not self.enable_caching or cache_key not in self.cache_timestamps:
            return False
        
        timestamp = self.cache_timestamps[cache_key]
        return (time.time() - timestamp) < self.cache_ttl
        
    def _get_cache_key(self, documents: List[Dict[str, str]], search_context: str) -> str:
        """Generate cache key for document processing"""
        content_hash = hashlib.md5(
            (str(documents) + search_context).encode()
        ).hexdigest()
        return f"doc_proc_{content_hash}"

    async def process_documents(self, 
                                documents: List[Dict[str, str]], 
                                search_context: str, 
                                title: str = None, 
                                category: str = None,
                                priority: str = "normal") -> List[Document]:
        """Process documents with enhanced error handling, caching, and performance optimizations."""
        
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(documents, search_context) if self.enable_caching else None
        if cache_key and self._is_cache_valid(cache_key):
            self.processing_stats['cache_hits'] += 1
            self.logger.info(f"@data_processor.py Cache hit for document processing")
            return self.cache[cache_key]
        
        if cache_key:
            self.processing_stats['cache_misses'] += 1
        
        self.logger.info(f"@data_processor.py Processing {len(documents)} documents with title={title} category={category} priority={priority}")
        self.doc_title = title
        self.doc_category = category

        # Validate input documents
        if not documents or not isinstance(documents, list):
            raise ValueError("Documents must be a non-empty list")
        
        # Filter out empty or invalid documents
        valid_documents = self._filter_valid_documents(documents)
        if not valid_documents:
            raise ValueError("No valid documents found after filtering")
        
        self.logger.info(f"@data_processor.py Processing {len(valid_documents)} valid documents after filtering")
        
        for attempt in range(self.max_processing_attempts):
            try:
                self.logger.info(f"@data_processor.py Starting document processing attempt {attempt + 1}")
                
                # Enhanced consolidation with async processing
                if self.enable_async_processing and len(valid_documents) > 5:
                    consolidated_text, refined_title = await self._consolidate_documents_async(valid_documents, search_context)
                else:
                    consolidated_text, refined_title = await self._consolidate_documents(valid_documents, search_context)
                
                self.doc_title = refined_title if refined_title != "Undefined" else title
                
                # Enhanced document creation with metadata
                document = self._create_processed_document_enhanced(consolidated_text, valid_documents, priority)
                
                # Enhanced splitting with content-aware chunking
                processed_documents = self._split_and_annotate_document_enhanced(document)
                
                processing_time = time.time() - start_time
                self.processing_stats['documents_processed'] += 1
                self.processing_stats['total_processing_time'] += processing_time
                
                self.logger.info(f"@data_processor.py Document processing completed in {processing_time:.2f} seconds. "
                            f"Generated {len(processed_documents)} document chunks.")
                
                # Cache the result
                if self.enable_caching and cache_key:
                    self.cache[cache_key] = processed_documents
                    self.cache_timestamps[cache_key] = time.time()
                
                return processed_documents

            except Exception as e:
                self.logger.error(f"@data_processor.py Document processing attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_processing_attempts - 1:
                    self.processing_stats['failed_documents'] += 1
                    return await self._generate_fallback_document_enhanced(valid_documents, e, priority)
                    
    def _filter_valid_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Filter out invalid or empty documents"""
        valid_docs = []
        for doc in documents:
            if isinstance(doc, dict) and 'content' in doc:
                content = doc['content'].strip()
                # Filter out very short content (likely noise)
                if len(content) > 10 and not self._is_spam_content(content):
                    valid_docs.append(doc)
                else:
                    self.logger.debug(f"@data_processor.py Filtered out document with content: {content[:50]}...")
            else:
                self.logger.warning(f"@data_processor.py Invalid document format: {type(doc)}")
        return valid_docs
        
    def _is_spam_content(self, content: str) -> bool:
        """Detect and filter spam or low-quality content"""
        spam_indicators = [
            len(content.split()) < 3,  # Too few words
            content.lower().count('click here') > 0,
            content.lower().count('buy now') > 0,
            content.count('!') > len(content) * 0.1,  # Too many exclamation marks
            re.match(r'^[\s\W]*$', content),  # Only whitespace/punctuation
        ]
        return any(spam_indicators)
        
    async def _consolidate_documents_async(self, documents: List[Dict[str, str]], search_context: str) -> Tuple[str, str]:
        """Asynchronously consolidate documents for better performance with large document sets"""
        
        # Process documents in batches
        batch_size = 5
        batches = [documents[i:i+batch_size] for i in range(0, len(documents), batch_size)]
        
        consolidated_texts = []
        for i, batch in enumerate(batches):
            self.logger.info(f"@data_processor.py Processing batch {i+1}/{len(batches)}")
            batch_content = "\n\n".join([doc['content'] for doc in batch])
            consolidated_texts.append(batch_content)
        
        # Combine all batch results
        all_content = "\n\n".join(consolidated_texts)
        
        # Apply final refinement
        try:
            refine_result = await self.asu_data_agent.refine(search_context, all_content)
            refined_content, refined_title = refine_result
            self.logger.info(f"@data_processor.py Async batch refinement successful")
            return refined_content.strip(), refined_title
        except Exception as e:
            self.logger.error(f"@data_processor.py Async batch refinement failed: {str(e)}")
            return all_content.strip(), "Batch Processed Content"

    def clean_and_structure_text(self, text: str) -> str:
        """Enhanced text cleaning for RAG applications."""
        if not text or not isinstance(text, str):
            return ""
            
        # Store emails and phone numbers before cleaning
        emails = self.EMAIL_PATTERN.findall(text)
        phones = self.PHONE_PATTERN.findall(text)
        
        # Remove HTML tags
        text = BeautifulSoup(text, "html.parser").get_text()

        # Remove links but preserve domain info
        links = self.LINK_PATTERN.findall(text)
        text = self.LINK_PATTERN.sub('[URL]', text)

        # Convert to ASCII and lowercase
        text = unidecode(text.lower())

        # Replace $ with USD
        text = text.replace('$', 'USD ')
        
        # Handle common abbreviations
        abbreviations = {
            ' asu ': ' arizona state university ',
            ' vs ': ' versus ',
            ' w/ ': ' with ',
            ' w/o ': ' without ',
            ' etc ': ' et cetera ',
            ' prof ': ' professor ',
            ' dept ': ' department ',
        }
        
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)

        # Remove special characters while preserving important punctuation
        text = self.SPECIAL_CHAR_PATTERN.sub(' ', text)

        # Tokenize and filter stopwords for better semantic understanding
        tokens = word_tokenize(text)
        filtered_tokens = []
        
        for token in tokens:
            if token.lower() not in self.stop_words or len(token) > 3:
                # Lemmatize meaningful words
                lemmatized = self.lemmatizer.lemmatize(token)
                filtered_tokens.append(lemmatized)

        # Rejoin tokens and normalize whitespace
        text = ' '.join(filtered_tokens)
        text = self.WHITESPACE_PATTERN.sub(' ', text).strip()
        
        # Restore important information
        if emails:
            text += f" Contact emails: {', '.join(emails)}"
        if phones:
            text += f" Phone numbers: {', '.join(phones)}"

        return text

    def _create_processed_document_enhanced(self, 
                                           consolidated_text: str, 
                                           documents: List[Dict[str, str]],
                                           priority: str = "normal") -> Document:
        """Create a processed document with enhanced metadata."""
        
        urls = []
        sources = []
        content_types = set()
        
        for doc in documents:
            if 'metadata' in doc:
                if 'url' in doc['metadata']:
                    urls.append(doc['metadata']['url'])
                if 'type' in doc['metadata']:
                    content_types.add(doc['metadata']['type'])
                if 'platform' in doc['metadata']:
                    sources.append(doc['metadata']['platform'])
        
        # Enhanced metadata
        metadata = {
            'title': self.doc_title or 'Untitled',
            'category': self.doc_category or "general",
            'url': urls[:5],  # Limit URLs
            'timestamp': datetime.now(),
            'total_source_documents': len(documents),
            'cluster_id': None,
            'priority': priority,
            'content_types': list(content_types),
            'sources': list(set(sources)),
            'processing_version': '2.0',  # Track processing improvements
            'word_count': len(consolidated_text.split()),
            'character_count': len(consolidated_text)
        }
        
        return Document(
            page_content=consolidated_text,
            metadata=metadata
        )

    def _split_and_annotate_document_enhanced(self, document: Document) -> List[Document]:
        """Enhanced document splitting with content-aware chunking."""
        min_chunk_length = 500
        content_length = len(document.page_content)
        
        # Use different strategies based on content length and type
        if content_length < min_chunk_length:
            # Short documents - don't split
            document.metadata.update({
                'id': str(uuid.uuid4()),
                'chunk_id': str(uuid.uuid4()),
                'chunk_index': 0,
                'total_chunks': 1,
                'chunk_type': 'complete_document'
            })
            return [document]
        
        # Determine optimal chunking strategy
        chunk_strategy = self._determine_chunk_strategy(document)
        
        if chunk_strategy == "semantic":
            return self._semantic_chunking(document)
        elif chunk_strategy == "paragraph":
            return self._paragraph_chunking(document)
        else:
            return self._standard_chunking(document)
    
    def _determine_chunk_strategy(self, document: Document) -> str:
        """Determine the best chunking strategy based on content analysis"""
        content = document.page_content
        
        # Count paragraphs (double newlines)
        paragraph_count = content.count('\n\n')
        
        # Check for structured content (lists, headers)
        has_structure = bool(re.search(r'^\d+\.|\*|\-', content, re.MULTILINE))
        
        # Check content category
        category = document.metadata.get('category', '').lower()
        
        if category in ['events_info', 'clubs_info'] and paragraph_count > 3:
            return "semantic"
        elif has_structure and paragraph_count > 2:
            return "paragraph"
        else:
            return "standard"
    
    def _semantic_chunking(self, document: Document) -> List[Document]:
        """Semantic-aware chunking for better context preservation"""
        try:
            from langchain_experimental.text_splitter import SemanticChunker
            from langchain_openai.embeddings import OpenAIEmbeddings
            
            semantic_splitter = SemanticChunker(
                embeddings=OpenAIEmbeddings(),
                breakpoint_threshold=0.5,
                chunk_size=1024,
                chunk_overlap=200
            )
            
            splits = semantic_splitter.split_documents([document])
            
            for i, split in enumerate(splits):
                split.metadata.update({
                    'id': str(uuid.uuid4()),
                    'chunk_id': str(uuid.uuid4()),
                    'chunk_index': i,
                    'total_chunks': len(splits),
                    'chunk_type': 'semantic',
                    'chunk_method': 'semantic_chunker'
                })
            
            return splits
            
        except Exception as e:
            self.logger.warning(f"@data_processor.py Semantic chunking failed: {str(e)}, falling back to standard")
            return self._standard_chunking(document)
    
    def _paragraph_chunking(self, document: Document) -> List[Document]:
        """Paragraph-aware chunking"""
        content = document.page_content
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) > 1024 and current_chunk:
                # Save current chunk
                chunk_doc = Document(
                    page_content=current_chunk.strip(),
                    metadata={
                        **document.metadata,
                        'id': str(uuid.uuid4()),
                        'chunk_id': str(uuid.uuid4()),
                        'chunk_index': chunk_index,
                        'chunk_type': 'paragraph',
                        'chunk_method': 'paragraph_aware'
                    }
                )
                chunks.append(chunk_doc)
                current_chunk = paragraph + "\n\n"
                chunk_index += 1
            else:
                current_chunk += paragraph + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunk_doc = Document(
                page_content=current_chunk.strip(),
                metadata={
                    **document.metadata,
                    'id': str(uuid.uuid4()),
                    'chunk_id': str(uuid.uuid4()),
                    'chunk_index': chunk_index,
                    'chunk_type': 'paragraph',
                    'chunk_method': 'paragraph_aware'
                }
            )
            chunks.append(chunk_doc)
        
        # Update total chunks
        for chunk in chunks:
            chunk.metadata['total_chunks'] = len(chunks)
        
        return chunks
    
    def _standard_chunking(self, document: Document) -> List[Document]:
        """Standard overlapping chunking"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        splits = text_splitter.split_documents([document])
        
        for i, split in enumerate(splits):
            split.metadata.update({
                'id': str(uuid.uuid4()),
                'chunk_id': str(uuid.uuid4()),
                'chunk_index': i,
                'total_chunks': len(splits),
                'chunk_type': 'standard',
                'chunk_method': 'recursive_character'
            })

        return splits

    async def _generate_fallback_document_enhanced(self, 
                                                  documents: List[Dict[str, str]], 
                                                  error: Exception,
                                                  priority: str = "normal") -> List[Document]:
        """Generate an enhanced fallback document when processing fails."""
        
        # Extract basic information even when processing fails
        all_content = []
        all_urls = []
        
        for doc in documents:
            if isinstance(doc, dict) and 'content' in doc:
                content = doc['content'][:500]  # Limit content to prevent issues
                all_content.append(content)
                
                if 'metadata' in doc and 'url' in doc['metadata']:
                    all_urls.append(doc['metadata']['url'])
        
        fallback_content = ' '.join(all_content)
        
        # Apply basic cleaning even in fallback
        try:
            fallback_content = self.clean_and_structure_text(fallback_content)
        except:
            # If even basic cleaning fails, use raw content
            fallback_content = ' '.join([doc.get('content', '') for doc in documents if isinstance(doc, dict)])
        
        fallback_doc = Document(
            page_content=fallback_content,
            metadata={
                'title': self.doc_title or 'Fallback Document',
                'category': self.doc_category or 'fallback',
                'url': all_urls[:5],
                'timestamp': datetime.now(),
                'error_message': str(error),
                'total_source_documents': len(documents),
                'processing_status': 'fallback',
                'priority': priority,
                'fallback_version': '2.0'
            }
        )

        return [fallback_doc]
    async def _consolidate_documents(self, documents: List[Dict[str, str]], search_context: str) -> str:
        """Consolidate all documents into a single text corpus and refine the combined content."""
        all_content = "\n\n".join([doc['content'] for doc in documents])
        refined_title = "Undefined"

        try:
            # Use DataModel to refine the combined content
            refine_result = await self.asu_data_agent.refine(search_context, all_content)
            refined_content, refined_title = refine_result
            self.logger.info(f"@data_processor.py Combined text refinement successful")
        except Exception as e:
            self.logger.error(f"@data_processor.py Combined text refinement failed: {str(e)}")
            refined_content = all_content  # Fallback to original combined content if refinement fails

        return refined_content.strip(), refined_title


    def _create_processed_document(self, 
                                   consolidated_text: str, 
                                   documents: List[Dict[str, str]]) -> Document:
        """Create a processed document with comprehensive metadata."""
        
        urls = []
        for doc in documents:
            if 'metadata' in doc and 'url' in doc['metadata']:
                urls.append(doc['metadata']['url'])
        
        return Document(
            page_content=consolidated_text,
            metadata={
                'title': self.doc_title or 'Untitled',
                'category': self.doc_category or "google_results",
                'url': urls[:5],  # Use the extracted URLs
                'timestamp': datetime.now(),
                'total_source_documents': len(documents),
                'cluster_id': None
            }
        )

    def _split_and_annotate_document(self, document: Document) -> List[Document]:
        """Split document into chunks and annotate with metadata."""
        min_chunk_length = 500  # Define the minimum length for chunking

        if len(document.page_content) < min_chunk_length:
            # If the document is too short, don't split it
            document.metadata.update({
                'id': str(uuid.uuid4()),
                'chunk_id': str(uuid.uuid4()),
                'chunk_index': 0,
                'total_chunks': 1  # Indicate that it's a single chunk
            })
            return [document]
        else:
            # Use SemanticTextSplitter to avoid splitting paragraphs abruptly

            # Create semantic splitter (adjust model as needed)
            semantic_splitter = SemanticChunker(
                embeddings=OpenAIEmbeddings(),
                breakpoint_threshold=0.5,  # Adjust as needed
                chunk_size=1024,
                chunk_overlap=200
            )
            
            # Proceed with splitting if the document is long enough
            splits = semantic_splitter.split_documents([document])

            for i, split in enumerate(splits):
                split.metadata.update({
                    'id': str(uuid.uuid4()),
                    'chunk_id': str(uuid.uuid4()),
                    'chunk_index': i,
                    'total_chunks': len(splits)
                })

            return splits

    async def _generate_fallback_document(self, 
                                          documents: List[Dict[str, str]], 
                                          error: Exception) -> List[Document]:
        """Generate a fallback document when all processing attempts fail."""
        fallback_doc = Document(
            page_content=' '.join([doc['content'] for doc in documents]),
            metadata={
                'title': self.doc_title or 'Fallback Document',
                'category': self.doc_category,
                'url': [doc['metadata']["url"] for doc in documents],
                'timestamp': datetime.now(),
                'error_message': str(error),
                'total_source_documents': len(documents)
            }
        )

        return [fallback_doc]
    
    async def process_documents_batch_async(self, documents: List[Dict], batch_size: int = 10) -> List[Dict]:
        """
        Process documents in batches asynchronously for better performance
        
        Args:
            documents: List of documents to process
            batch_size: Size of each processing batch
            
        Returns:
            List of processed documents
        """
        try:
            if not documents:
                return []
            
            self.logger.info(f"@data_processor.py Processing {len(documents)} documents in batches of {batch_size}")
            
            all_results = []
            
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                batch_results = []
                
                # Process batch documents
                for doc in batch:
                    if isinstance(doc, dict) and 'content' in doc:
                        try:
                            # Convert to expected format
                            formatted_doc = {
                                'content': doc['content'],
                                'metadata': doc.get('metadata', {}),
                                'title': doc.get('title', ''),
                                'category': doc.get('category', 'general')
                            }
                            
                            # Process the document
                            result = self.process_documents([formatted_doc])
                            if result:
                                all_results.extend(result)
                                
                        except Exception as e:
                            self.logger.error(f"@data_processor.py Error processing document in batch: {str(e)}")
                            continue
                
                self.logger.debug(f"@data_processor.py Processed batch {i//batch_size + 1}")
            
            self.performance_metrics['documents_processed'] += len(documents)
            self.logger.info(f"@data_processor.py Batch processing completed: {len(all_results)} chunks generated")
            
            return all_results
            
        except Exception as e:
            self.logger.error(f"@data_processor.py Error in batch processing: {str(e)}")
            return []
    
    def _clean_text_enhanced(self, text: str) -> str:
        """
        Enhanced text cleaning with better handling of various content types
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        try:
            if not text:
                return ""
            
            # Preserve important formatting while cleaning
            
            # Step 1: Normalize whitespace but preserve paragraph structure
            text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
            text = re.sub(r'[ \t]+', ' ', text)     # Normalize spaces/tabs
            
            # Step 2: Clean HTML entities and tags
            import html
            text = html.unescape(text)
            text = re.sub(r'<[^>]+>', ' ', text)
            
            # Step 3: Preserve important patterns (emails, phones, URLs)
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            url_pattern = r'https?://[^\s]+|www\.[^\s]+'
            
            # Step 4: Remove excessive punctuation
            text = re.sub(r'[^\w\s\.\!\?\,\:\;\-\(\)@]+', ' ', text)
            
            # Step 5: Fix spacing around punctuation
            text = re.sub(r'\s+([\.!\?])', r'\1', text)
            text = re.sub(r'\s*,\s*', ', ', text)
            
            # Step 6: Remove excessive whitespace
            text = re.sub(r'\s{2,}', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"@data_processor.py Error in enhanced text cleaning: {str(e)}")
            return text
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        metrics = self.performance_metrics.copy()
        
        # Add cache statistics
        if hasattr(self, 'chunk_cache'):
            metrics['cache_size'] = len(self.chunk_cache)
            metrics['cache_hit_rate'] = (
                metrics['cache_hits'] / (metrics['cache_hits'] + metrics['cache_misses']) 
                if (metrics['cache_hits'] + metrics['cache_misses']) > 0 else 0
            )
        
        return metrics