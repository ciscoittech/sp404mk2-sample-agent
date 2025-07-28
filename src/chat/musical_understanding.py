"""
Musical understanding module - Translates natural language to structured musical queries.
Uses specialist knowledge to enhance understanding.
"""

from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field
import re


class MusicalRequest(BaseModel):
    """Structured representation of a musical request."""
    
    # Core musical attributes
    genres: List[str] = Field(default_factory=list, description="Musical genres")
    sub_genres: List[str] = Field(default_factory=list, description="Sub-genres or styles")
    
    # Temporal attributes
    era: Optional[str] = Field(None, description="Time period")
    year_range: Optional[Tuple[int, int]] = Field(None, description="Specific year range")
    
    # Musical characteristics
    bpm_range: Optional[Tuple[int, int]] = Field(None, description="Tempo range")
    key: Optional[str] = Field(None, description="Musical key")
    mood: Optional[str] = Field(None, description="Emotional quality")
    energy_level: Optional[str] = Field(None, description="Energy level (low/medium/high)")
    
    # Production characteristics
    production_style: Optional[str] = Field(None, description="Production approach")
    equipment_references: List[str] = Field(default_factory=list, description="Specific gear")
    texture_descriptors: List[str] = Field(default_factory=list, description="Sonic textures")
    
    # References
    artist_references: List[str] = Field(default_factory=list, description="Artist/producer references")
    track_references: List[str] = Field(default_factory=list, description="Specific track references")
    
    # Technical details
    sample_types: List[str] = Field(default_factory=list, description="Types of samples needed")
    groove_characteristics: Dict[str, Any] = Field(default_factory=dict, description="Groove details")
    
    # Generated search queries
    search_queries: List[str] = Field(default_factory=list, description="Generated search terms")
    youtube_queries: List[str] = Field(default_factory=list, description="YouTube-specific queries")


class MusicalUnderstanding:
    """Translates natural language to structured musical queries using specialist knowledge."""
    
    def __init__(self):
        # Vibe to technical translations (from musical-search-specialist)
        self.vibe_translations = {
            "dusty": ["vinyl", "lo-fi", "tape", "analog", "vintage", "old school"],
            "smooth": ["silk", "liquid", "mellow", "warm", "laid back", "relaxed"],
            "crunchy": ["distorted", "saturated", "bit-crushed", "compressed", "gritty"],
            "spacey": ["ambient", "ethereal", "cosmic", "reverb", "atmospheric", "floating"],
            "bouncy": ["groovy", "funky", "rhythmic", "percussive", "upbeat", "energetic"],
            "dark": ["moody", "ominous", "heavy", "deep", "shadowy", "mysterious"],
            "bright": ["crisp", "clear", "shimmering", "sparkling", "airy", "light"],
            "warm": ["analog", "tube", "vintage", "mellow", "rich", "full"],
            "cold": ["digital", "metallic", "stark", "clinical", "precise", "sharp"],
            "raw": ["unprocessed", "rough", "gritty", "unpolished", "live", "organic"]
        }
        
        # Producer style mappings (from groove-analyst and era-expert)
        self.producer_styles = {
            "dilla": {
                "bpm_range": (85, 95),
                "swing": "drunk",
                "characteristics": ["off-grid", "wonky", "humanized"],
                "equipment": ["MPC3000", "SP1200"],
                "search_terms": ["dilla drums", "detroit hip hop", "slum village"]
            },
            "madlib": {
                "characteristics": ["dusty", "psychedelic", "jazzy"],
                "search_terms": ["obscure samples", "loop digga", "quasimoto"],
                "genres": ["jazz", "soul", "psych", "world"]
            },
            "premier": {
                "bpm_range": (90, 100),
                "characteristics": ["chopped", "scratched", "hard"],
                "search_terms": ["boom bap", "gang starr", "NY hip hop"],
                "equipment": ["MPC60", "Technics 1200"]
            },
            "flying lotus": {
                "characteristics": ["glitchy", "experimental", "cosmic"],
                "search_terms": ["future beats", "brainfeeder", "cosmogramma"],
                "genres": ["electronic", "jazz", "experimental"]
            },
            "kaytranada": {
                "bpm_range": (100, 125),
                "characteristics": ["bouncy", "filtered", "danceable"],
                "search_terms": ["future funk", "dance soul", "haiti groove"],
                "genres": ["house", "funk", "soul", "disco"]
            }
        }
        
        # Era characteristics (from era-expert)
        self.era_mappings = {
            "60s": {
                "years": (1960, 1969),
                "characteristics": ["mono", "live recording", "tape"],
                "search_terms": ["1960s", "sixties", "motown", "stax"]
            },
            "70s": {
                "years": (1970, 1979),
                "characteristics": ["analog", "funk", "disco", "soul"],
                "search_terms": ["1970s", "seventies", "vintage funk"]
            },
            "80s": {
                "years": (1980, 1989),
                "characteristics": ["digital", "synth", "drum machine"],
                "search_terms": ["1980s", "eighties", "synthwave"]
            },
            "90s": {
                "years": (1990, 1999),
                "characteristics": ["sampling", "boom bap", "golden era"],
                "search_terms": ["1990s", "nineties", "classic hip hop"]
            },
            "2000s": {
                "years": (2000, 2009),
                "characteristics": ["digital", "crisp", "loud"],
                "search_terms": ["2000s", "y2k", "ringtone era"]
            }
        }
    
    def parse_request(self, text: str) -> MusicalRequest:
        """Parse natural language into structured musical request."""
        request = MusicalRequest()
        text_lower = text.lower()
        
        # Extract BPM if mentioned
        bpm_match = re.search(r'(\d+)\s*(?:-|to)\s*(\d+)\s*bpm', text_lower)
        if not bpm_match:
            bpm_match = re.search(r'(\d+)\s*bpm', text_lower)
            if bpm_match:
                bpm = int(bpm_match.group(1))
                request.bpm_range = (bpm - 5, bpm + 5)
        else:
            request.bpm_range = (int(bpm_match.group(1)), int(bpm_match.group(2)))
        
        # Check for producer references
        for producer, style in self.producer_styles.items():
            if producer in text_lower:
                request.artist_references.append(producer)
                if "bpm_range" in style and not request.bpm_range:
                    request.bpm_range = style["bpm_range"]
                request.texture_descriptors.extend(style.get("characteristics", []))
                request.search_queries.extend(style.get("search_terms", []))
        
        # Check for era references
        for era, mapping in self.era_mappings.items():
            if era in text_lower:
                request.era = era
                request.year_range = mapping["years"]
                request.texture_descriptors.extend(mapping["characteristics"])
                request.search_queries.extend(mapping["search_terms"])
        
        # Check for vibe descriptors
        for vibe, translations in self.vibe_translations.items():
            if vibe in text_lower:
                request.texture_descriptors.append(vibe)
                request.search_queries.extend(translations[:2])  # Add top 2 translations
        
        # Extract sample types
        sample_keywords = {
            "drums": ["drums", "breaks", "beats", "percussion"],
            "bass": ["bass", "bassline", "sub", "low end"],
            "keys": ["keys", "piano", "rhodes", "wurlitzer", "organ"],
            "melody": ["melody", "melodic", "lead", "riff"],
            "vocal": ["vocal", "vox", "voice", "acapella"],
            "pad": ["pad", "atmosphere", "ambient", "texture"]
        }
        
        for sample_type, keywords in sample_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                request.sample_types.append(sample_type)
        
        # Extract genres
        genre_keywords = {
            "hip hop": ["hip hop", "hip-hop", "hiphop", "boom bap", "trap"],
            "jazz": ["jazz", "bebop", "swing", "fusion"],
            "soul": ["soul", "r&b", "rnb", "motown"],
            "funk": ["funk", "funky", "groove"],
            "electronic": ["electronic", "edm", "house", "techno", "drum and bass"],
            "rock": ["rock", "indie", "punk", "metal"],
            "reggae": ["reggae", "dub", "dancehall"],
            "latin": ["latin", "salsa", "bossa", "afrobeat"]
        }
        
        for genre, keywords in genre_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                request.genres.append(genre)
        
        # Generate enhanced search queries
        request.search_queries = self._generate_search_queries(request)
        request.youtube_queries = self._generate_youtube_queries(request)
        
        return request
    
    def _generate_search_queries(self, request: MusicalRequest) -> List[str]:
        """Generate comprehensive search queries from parsed request."""
        queries = []
        
        # Base query components
        components = []
        
        if request.genres:
            components.append(request.genres[0])
        
        if request.sample_types:
            components.append(request.sample_types[0])
        
        if request.era:
            components.append(request.era)
        
        # Create base query
        if components:
            base_query = " ".join(components)
            queries.append(base_query)
            
            # Add variations
            if request.texture_descriptors:
                for descriptor in request.texture_descriptors[:2]:
                    queries.append(f"{base_query} {descriptor}")
            
            if request.bpm_range:
                queries.append(f"{base_query} {request.bpm_range[0]}-{request.bpm_range[1]} BPM")
            
            if request.artist_references:
                for artist in request.artist_references:
                    queries.append(f"{base_query} {artist} style")
        
        # Add any existing queries
        queries.extend(request.search_queries)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)
        
        return unique_queries[:10]  # Limit to 10 queries
    
    def _generate_youtube_queries(self, request: MusicalRequest) -> List[str]:
        """Generate YouTube-specific search queries."""
        youtube_queries = []
        
        base_queries = request.search_queries[:3]  # Top 3 general queries
        
        for query in base_queries:
            # Add YouTube-specific terms
            youtube_queries.extend([
                f"{query} sample pack",
                f"{query} free download",
                f"{query} type beat",
                f"{query} loop kit"
            ])
        
        return youtube_queries[:8]  # Limit to 8 YouTube queries


# Example usage
if __name__ == "__main__":
    understanding = MusicalUnderstanding()
    
    # Test various requests
    test_requests = [
        "I need that Dilla bounce around 90 BPM",
        "Find me some dusty 70s soul breaks",
        "Looking for smooth jazz keys, something like Robert Glasper",
        "I want aggressive trap drums, really crunchy and distorted",
        "Show me some Madlib-style psychedelic loops"
    ]
    
    for request_text in test_requests:
        print(f"\nRequest: {request_text}")
        parsed = understanding.parse_request(request_text)
        print(f"Genres: {parsed.genres}")
        print(f"BPM Range: {parsed.bpm_range}")
        print(f"Descriptors: {parsed.texture_descriptors}")
        print(f"Search Queries: {parsed.search_queries[:3]}...")
        print("-" * 50)