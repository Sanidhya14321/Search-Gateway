export type Citation = {
  url: string;
  fetched_at?: string;
  trust_score?: number;
};

export type SearchCandidate = {
  canonical_id: string;
  canonical_name: string;
  confidence: number;
  match_type?: string;
  domain?: string;
};

export type SearchResponse = {
  query: string;
  candidates: SearchCandidate[];
  context_preview?: Array<{ chunk_text: string; source_url?: string }>;
};
