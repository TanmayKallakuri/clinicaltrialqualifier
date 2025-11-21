# skyflow_manager.py - Mock Skyflow integration for demo

class SkyflowManager:
    """
    Mock Skyflow manager for demonstration purposes

    In production, this would connect to actual Skyflow vault
    For hackathon demo, simulates tokenization behavior
    """

    def __init__(self):
        self.token_store = {}
        self.token_counter = 0

    def tokenize_batch(self, studies):
        """
        Tokenize sensitive fields in studies

        In production: sends to Skyflow vault
        Demo mode: simulates tokenization
        """
        tokenized_studies = []

        for study in studies:
            tokenized = study.copy()

            # Mark as protected
            tokenized['_skyflow_protected'] = True

            # Tokenize sensitive fields
            if 'lead_sponsor' in tokenized and tokenized['lead_sponsor']:
                token = self._generate_token()
                self.token_store[token] = tokenized['lead_sponsor']
                tokenized['lead_sponsor'] = f"[TOKENIZED:{token}]"

            if 'investigators' in tokenized and tokenized['investigators']:
                tokenized_investigators = []
                for investigator in tokenized['investigators']:
                    token = self._generate_token()
                    self.token_store[token] = investigator
                    tokenized_investigators.append(f"[TOKENIZED:{token}]")
                tokenized['investigators'] = tokenized_investigators

            if 'sites' in tokenized and tokenized['sites']:
                tokenized_sites = []
                for site in tokenized['sites']:
                    token = self._generate_token()
                    self.token_store[token] = site
                    tokenized_sites.append(f"[TOKENIZED:{token}]")
                tokenized['sites'] = tokenized_sites

            tokenized_studies.append(tokenized)

        return tokenized_studies

    def detokenize_study(self, study):
        """
        Detokenize a study

        In production: requires authorization + vault access
        Demo mode: returns original values
        """
        detokenized = study.copy()

        # Detokenize lead_sponsor
        if 'lead_sponsor' in detokenized:
            sponsor = detokenized['lead_sponsor']
            if isinstance(sponsor, str) and sponsor.startswith('[TOKENIZED:'):
                token = sponsor.replace('[TOKENIZED:', '').replace(']', '')
                detokenized['lead_sponsor'] = self.token_store.get(token, sponsor)

        # Detokenize investigators
        if 'investigators' in detokenized:
            original_investigators = []
            for investigator in detokenized['investigators']:
                if isinstance(investigator, str) and investigator.startswith('[TOKENIZED:'):
                    token = investigator.replace('[TOKENIZED:', '').replace(']', '')
                    original_investigators.append(self.token_store.get(token, investigator))
                else:
                    original_investigators.append(investigator)
            detokenized['investigators'] = original_investigators

        # Detokenize sites
        if 'sites' in detokenized:
            original_sites = []
            for site in detokenized['sites']:
                if isinstance(site, str) and site.startswith('[TOKENIZED:'):
                    token = site.replace('[TOKENIZED:', '').replace(']', '')
                    original_sites.append(self.token_store.get(token, site))
                else:
                    original_sites.append(site)
            detokenized['sites'] = original_sites

        detokenized['_skyflow_protected'] = False

        return detokenized

    def get_stats(self):
        """Get tokenization statistics"""
        return {
            "total_tokens": self.token_counter,
            "vault_size": len(self.token_store),
            "status": "active (demo mode)"
        }

    def _generate_token(self):
        """Generate a unique token ID"""
        self.token_counter += 1
        return f"sky_{self.token_counter:06d}"


# Global instance
skyflow = SkyflowManager()
