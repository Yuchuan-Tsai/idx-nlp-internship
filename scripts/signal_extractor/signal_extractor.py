"""Signal extraction helpers for listing remarks (Week 6)."""

import re


class SignalExtractor:
    """Extract structured signals from listing remarks."""

    def __init__(self, taxonomy, entity_extractor):
        self.taxonomy = taxonomy
        self.extractor = entity_extractor

        self.amenity_terms = self._flatten_taxonomy_terms(taxonomy)

        self.condition_patterns = {
            'move-in ready': [r'move\s*-?in\s+ready', r'turn\s*-?key', r'ready\s+to\s+move\s+in'],
            'new construction': [r'new\s+construction', r'brand\s+new', r'newly\s+built'],
            'renovated': [r'fully\s+renovated', r'recently\s+renovated', r'remodeled', r'updated'],
            'fixer': [r'fixer', r'fixer\s*upper', r'tlc\s+needed', r'handyman\s+special'],
            'as-is': [r'as\s*-?is'],
            'original condition': [r'original\s+condition'],
            'well maintained': [r'well\s+maintained', r'pride\s+of\s+ownership', r'immaculate']
        }

        self.financing_patterns = {
            'cash': [r'cash\s+only', r'cash\s+buyer'],
            'conventional': [r'conventional\s+loan', r'conv\s+loan', r'conventional\s+financing'],
            'fha': [r'\bfha\b', r'fha\s+financing'],
            'va': [r'\bva\b', r'va\s+loan', r'va\s+financing'],
            'usda': [r'\busda\b'],
            'seller financing': [r'seller\s+financing', r'owner\s+financing', r'owner\s+carry'],
            'assumable': [r'assumable\s+(?:loan|mortgage)'],
            '1031 exchange': [r'1031\s+exchange'],
            'lease option': [r'lease\s+option', r'rent\s+to\s+own']
        }

        self.location_patterns = {
            'near schools': [r'near\s+schools?', r'close\s+to\s+schools?'],
            'walking distance': [r'walking\s+distance\s+to', r'walk\s+to'],
            'close to shopping': [r'close\s+to\s+shopping', r'near\s+shopping', r'shopping\s+and\s+dining'],
            'close to freeway': [r'easy\s+access\s+to\s+freeway', r'freeway\s+access', r'highway\s+access'],
            'quiet neighborhood': [r'quiet\s+neighborhood'],
            'cul-de-sac': [r'cul\s*-?de\s*-?sac'],
            'corner lot': [r'corner\s+lot'],
            'waterfront': [r'waterfront', r'lakefront', r'river\s+access'],
            'views': [r'ocean\s+view', r'mountain\s+view', r'city\s+view', r'panoramic\s+views?', r'scenic\s+views?'],
            'downtown': [r'near\s+downtown', r'close\s+to\s+downtown', r'\bdowntown\b']
        }

    def extract_signals(self, listing_record):
        remarks = self._normalize_text(
            listing_record.get('L_Remarks', listing_record.get('remarks', ''))
        )

        entities = self.extractor.extract_all(remarks)
        amenities = self._match_amenities(remarks)

        return {
            'listing_id': listing_record.get('L_ListingID', listing_record.get('listing_id')),
            'entities': entities,
            'amenities': amenities,
            'condition_keywords': self._extract_condition(remarks),
            'financing_terms': self._extract_financing(remarks),
            'location_features': self._extract_location(remarks)
        }

    def _normalize_text(self, text):
        return ' '.join(str(text).split()) if text else ''

    def _flatten_taxonomy_terms(self, taxonomy):
        if not taxonomy:
            return []

        terms = []
        if isinstance(taxonomy, dict) and 'terms' in taxonomy:
            for item in taxonomy.get('terms', []):
                term = item.get('term') if isinstance(item, dict) else None
                if term:
                    terms.append(term)
        elif isinstance(taxonomy, dict):
            for value in taxonomy.values():
                if isinstance(value, list):
                    terms.extend(value)

        deduped = []
        seen = set()
        for term in terms:
            t = str(term).strip().lower()
            if t and t not in seen:
                seen.add(t)
                deduped.append(t)

        deduped.sort(key=len, reverse=True)
        return deduped

    def _match_amenities(self, remarks):
        text = remarks.lower()
        found = []
        for term in self.amenity_terms:
            pattern = rf'(?<!\w){re.escape(term)}(?!\w)'
            if re.search(pattern, text, flags=re.I):
                found.append(term)
        return sorted(set(found))

    def _extract_condition(self, remarks):
        return self._extract_by_patterns(remarks, self.condition_patterns)

    def _extract_financing(self, remarks):
        return self._extract_by_patterns(remarks, self.financing_patterns)

    def _extract_location(self, remarks):
        return self._extract_by_patterns(remarks, self.location_patterns)

    def _extract_by_patterns(self, text, pattern_map):
        hits = []
        for canonical, patterns in pattern_map.items():
            for pattern in patterns:
                if re.search(pattern, text, flags=re.I):
                    hits.append(canonical)
                    break
        return sorted(set(hits))
