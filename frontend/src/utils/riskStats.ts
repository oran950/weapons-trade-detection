import type { Post } from '../context/AppContext';

export interface RiskStats {
  totalAnalyzed: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;
}

/** Derive dashboard counters from the posts list (single source of truth). */
export function computeRiskStats(posts: Post[]): RiskStats {
  let highRiskCount = 0;
  let mediumRiskCount = 0;
  let lowRiskCount = 0;

  for (const post of posts) {
    const level = post.risk_analysis?.risk_level;
    if (level === 'HIGH' || level === 'CRITICAL') {
      highRiskCount += 1;
    } else if (level === 'MEDIUM') {
      mediumRiskCount += 1;
    } else {
      // LOW, NONE, or missing — still a collected/analyzed post
      lowRiskCount += 1;
    }
  }

  return {
    totalAnalyzed: posts.length,
    highRiskCount,
    mediumRiskCount,
    lowRiskCount,
  };
}
