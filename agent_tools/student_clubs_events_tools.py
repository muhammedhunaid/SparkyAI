from utils.common_imports import *

class Student_Clubs_Events_Agent_Tools:
    def __init__(self,middleware,utils,logger):
        self.middleware = middleware
        self.utils = utils
        self.visited_urls = set()
        self.max_depth = 2
        self.max_links_per_page = 3
        self.use_sundevil_central = True  # Feature flag for SunDevilCentral migration
        self.sundevilcentral_url = "https://sundevilcentral.asu.edu"  # New platform URL
        
    def _get_base_url(self, url_type: str = "organizations") -> str:
        """
        Get the base URL for either SunDevilCentral (new) or SunDevilSync (legacy)
        """
        if self.use_sundevil_central:
            # New SunDevilCentral platform
            if url_type == "organizations":
                return "https://central.asu.edu/organizations"
            elif url_type == "events":
                return "https://central.asu.edu/events"
            else:
                return "https://central.asu.edu"
        else:
            # Legacy SunDevilSync platform
            if url_type == "organizations":
                return "https://asu.campuslabs.com/engage/organizations"
            elif url_type == "events":
                return "https://asu.campuslabs.com/engage/events"
            else:
                return "https://asu.campuslabs.com/engage"
        
        async def get_latest_event_updates(self, search_bar_query: str = None, event_category: list = None, 
                                    event_theme: list = None, event_campus: list = None, 
                                    shortcut_date: str = None, event_perk: list = None):
                
                if not any([search_bar_query, event_category, event_theme, event_campus]):
                    return "At least one parameter of this function is required. Neither Search query and organization category and organization campus received. Please provide at least one parameter to perform search."
                
                # Get base URL based on platform
                search_url = self._get_base_url("events")
                
                # Handle different URL structures for different platforms
                if self.use_sundevil_central:
                    # SunDevilCentral uses different parameter structure
                    params = self._build_central_event_params(search_bar_query, event_category, event_theme, event_campus, shortcut_date, event_perk)
                else:
                    # Legacy SunDevilSync parameters
                    params = self._build_legacy_event_params(search_bar_query, event_category, event_theme, event_campus, shortcut_date, event_perk)
                
                if params:
                    search_url += "?" + "&".join(params)
                
                # Build document title
                doc_title = self._build_doc_title(search_bar_query, event_category, event_theme, event_campus, shortcut_date, event_perk)
                
                return await self.utils.perform_web_search(search_url, doc_title=doc_title, doc_category = "events_info")
    
    def _build_central_event_params(self, search_bar_query, event_category, event_theme, event_campus, shortcut_date, event_perk):
        """Build URL parameters for SunDevilCentral platform"""
        params = []
        
        # SunDevilCentral uses different parameter names and values
        central_campus_mapping = {
            "ASU Downtown": "downtown",
            "ASU Online": "online", 
            "ASU Polytechnic": "polytechnic",
            "ASU Tempe": "tempe",
            "ASU West Valley": "west",
            "Fraternity & Sorority Life": "greek",
            "Housing & Residential Life": "housing"
        }
        
        central_category_mapping = {
            "ASU New Student Experience": "new-student",
            "ASU Sync": "sync",
            "Career and Professional Development": "career",
            "Club Meetings": "meetings",
            "Community Service": "service",
            "Cultural": "cultural",
            "Graduate": "graduate", 
            "International": "international",
            "Social": "social",
            "Sports/Recreation": "sports",
            "Sustainability": "sustainability"
        }
        
        if search_bar_query:
            params.append(f"search={search_bar_query.replace(' ', '+')}")
        
        if event_campus:
            for campus in event_campus:
                if campus in central_campus_mapping:
                    params.append(f"campus={central_campus_mapping[campus]}")
        
        if event_category:
            for category in event_category:
                if category in central_category_mapping:
                    params.append(f"category={central_category_mapping[category]}")
        
        if shortcut_date:
            if shortcut_date.lower() == "tomorrow":
                params.append("date=tomorrow")
            elif shortcut_date.lower() == "this_weekend":
                params.append("date=weekend")
        
        return params

    def _build_legacy_event_params(self, search_bar_query, event_category, event_theme, event_campus, shortcut_date, event_perk):
        """Build URL parameters for legacy SunDevilSync platform"""
        params = []
        
        # Legacy parameter mappings (existing logic)
        event_campus_ids = {
            "ASU Downtown": "257211",
            "ASU Online": "257214", 
            "ASU Polytechnic": "257212",
            "ASU Tempe": "254417",
            "ASU West Valley": "257213",
            "Fraternity & Sorority Life": "257216",
            "Housing & Residential Life": "257215"
        }
        
        event_category_ids = {
            "ASU New Student Experience": "18002",
            "ASU Sync": "15695",
            "ASU Welcome Event": "12897",
            "Barrett Student Organization": "12902",
            "Career and Professional Development": "12885",
            "Club Meetings": "12887",
            "Community Service": "12903",
            "Cultural": "12898",
            "Graduate": "12906",
            "International": "12899",
            "Social": "12892",
            "Sports/Recreation": "12894",
            "Sustainability": "12905"
        }
        
        event_theme_ids = {
            "Arts": "arts",
            "Athletics": "athletics",
            "Community Service": "community_service",
            "Cultural": "cultural",
            "Fundraising": "fundraising",
            "GroupBusiness": "group_business",
            "Social": "social",
            "Spirituality": "spirituality",
            "ThoughtfulLearning": "thoughtful_learning"
        }
        
        event_perk_ids = {
            "Credit": "Credit",
            "Free Food": "FreeFood",
            "Free Stuff": "FreeStuff"
        }
        
        if event_campus:
            campus_id_array = [event_campus_ids[campus] for campus in event_campus if campus in event_campus_ids]
            if campus_id_array:
                params.extend([f"branches={campus_id}" for campus_id in campus_id_array])
        
        if event_category:
            category_id_array = [event_category_ids[category] for category in event_category if category in event_category_ids]
            if category_id_array:
                params.extend([f"categories={category_id}" for category_id in category_id_array])
        
        if event_theme:
            theme_id_array = [event_theme_ids[theme] for theme in event_theme if theme in event_theme_ids]
            if theme_id_array:
                params.extend([f"themes={theme_id}" for theme_id in theme_id_array])
        
        if event_perk:
            perk_id_array = [event_perk_ids[perk] for perk in event_perk if perk in event_perk_ids]
            if perk_id_array:
                params.extend([f"perks={perk_id}" for perk_id in perk_id_array])
        
        if shortcut_date:
            valid_dates = ["tomorrow", "this_weekend"]
            if shortcut_date.lower() in valid_dates:
                params.append(f"shortcutdate={shortcut_date.lower()}")
        
        if search_bar_query:
            params.append(f"query={search_bar_query.lower().replace(' ', '%20')}")
        
        return params

    def _build_doc_title(self, search_bar_query, event_category, event_theme, event_campus, shortcut_date, event_perk):
        """Build document title for search results"""
        if search_bar_query:
            return search_bar_query
        elif event_category:
            return " ".join(event_category)
        elif event_theme:
            return " ".join(event_theme)
        elif event_campus:
            return " ".join(event_campus)
        elif shortcut_date:
            return shortcut_date
        elif event_perk:
            return " ".join(event_perk)
        else:
            return "Events"

    async def get_latest_club_information(self, search_bar_query: str = None, organization_category: list = None, organization_campus: list = None):
        if not any([search_bar_query, organization_category, organization_campus]):
            return "At least one parameter of this function is required. Neither Search query and organization category and organization campus received. Please provide at least one parameter to perform search."
        
        # Get base URL based on platform
        search_url = self._get_base_url("organizations")
        
        # Handle different URL structures for different platforms
        if self.use_sundevil_central:
            # SunDevilCentral uses different parameter structure
            params = self._build_central_org_params(search_bar_query, organization_category, organization_campus)
        else:
            # Legacy SunDevilSync parameters
            params = self._build_legacy_org_params(search_bar_query, organization_category, organization_campus)
        
        if params:
            search_url += "?" + "&".join(params)
        
        # Build document title
        doc_title = self._build_org_doc_title(search_bar_query, organization_category, organization_campus)
        
        return await self.utils.perform_web_search(search_url, doc_title=doc_title, doc_category="clubs_info")

    def _build_central_org_params(self, search_bar_query, organization_category, organization_campus):
        """Build URL parameters for SunDevilCentral organizations"""
        params = []
        
        # SunDevilCentral campus mapping
        central_campus_mapping = {
            "ASU Downtown": "downtown",
            "ASU Online": "online",
            "ASU Polytechnic": "polytechnic", 
            "ASU Tempe": "tempe",
            "ASU West Valley": "west",
            "Fraternity & Sorority Life": "greek",
            "Housing & Residential Life": "housing"
        }
        
        # SunDevilCentral category mapping (simplified)
        central_category_mapping = {
            "Academic": "academic",
            "Barrett": "barrett",
            "Creative/Performing Arts": "arts",
            "Cultural/Ethnic": "cultural",
            "Graduate": "graduate",
            "Health/Wellness": "health",
            "International": "international",
            "LGBTQIA+": "lgbtq",
            "Political": "political", 
            "Professional": "professional",
            "Religious/Faith/Spiritual": "religious",
            "Service": "service",
            "Social Awareness": "social-awareness",
            "Special Interest": "special-interest",
            "Sports/Recreation": "sports",
            "Sustainability": "sustainability",
            "Technology": "technology",
            "Veteran Groups": "veterans",
            "Women": "women"
        }
        
        if search_bar_query:
            params.append(f"search={search_bar_query.replace(' ', '+')}")
        
        if organization_campus:
            for campus in organization_campus:
                if campus in central_campus_mapping:
                    params.append(f"campus={central_campus_mapping[campus]}")
        
        if organization_category:
            for category in organization_category:
                if category in central_category_mapping:
                    params.append(f"category={central_category_mapping[category]}")
        
        return params

    def _build_legacy_org_params(self, search_bar_query, organization_category, organization_campus):
        """Build URL parameters for legacy SunDevilSync organizations"""
        params = []
        
        # Legacy parameter mappings
        organization_campus_ids = {
            "ASU Downtown": "257211",
            "ASU Online": "257214",
            "ASU Polytechnic": "257212",
            "ASU Tempe": "254417",
            "ASU West Valley": "257213",
            "Fraternity & Sorority Life": "257216",
            "Housing & Residential Life": "257215"
        }
        
        organization_category_ids = {
            "Academic": "13382",
            "Barrett": "14598",
            "Creative/Performing Arts": "13383",
            "Cultural/Ethnic": "13384",
            "Distinguished Student Organization": "14549",
            "Graduate": "13387",
            "Health/Wellness": "13388",
            "International": "13389",
            "LGBTQIA+": "13391",
            "Political": "13392",
            "Professional": "13393",
            "Religious/Faith/Spiritual": "13395",
            "Service": "13396",
            "Social Awareness": "13398",
            "Special Interest": "13399",
            "Sports/Recreation": "13400",
            "Sustainability": "13402",
            "Technology": "13403",
            "Veteran Groups": "14569",
            "Women": "13405"
        }
        
        if organization_campus:
            campus_id_array = [organization_campus_ids[campus] for campus in organization_campus if campus in organization_campus_ids]
            if campus_id_array:
                params.extend([f"branches={campus_id}" for campus_id in campus_id_array])
        
        if organization_category:
            category_id_array = [organization_category_ids[category] for category in organization_category if category in organization_category_ids]
            if category_id_array:
                params.extend([f"categories={category_id}" for category_id in category_id_array])
        
        if search_bar_query:
            params.append(f"query={search_bar_query.lower().replace(' ', '%20')}")
        
        return params

    def _build_org_doc_title(self, search_bar_query, organization_category, organization_campus):
        """Build document title for organization search results"""
        if search_bar_query:
            return search_bar_query
        elif organization_category:
            return " ".join(organization_category)
        elif organization_campus:
            return " ".join(organization_campus)
        else:
            return "Organizations"
        
  
