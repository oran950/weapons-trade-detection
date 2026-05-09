import type { CollectionSession, Post } from '../context/AppContext';
import type { OsintPdfDigestPayload } from '../types';

/** Strip heavy fields before sending posts to the PDF API. */
export function postToPdfJson(post: Post): Record<string, unknown> {
  return {
    id: post.id,
    title: post.title,
    content: (post.content || '').slice(0, 8000),
    platform: post.platform,
    subreddit: post.subreddit,
    channel: post.channel,
    url: post.url,
    author_hash: post.author_hash,
    collected_at: post.collected_at,
    risk_analysis: post.risk_analysis,
    llm_analysis: post.llm_analysis,
    image_analysis: post.image_analysis,
  };
}

export interface DigestStatsShape {
  totalAnalyzed: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;
  platformsMonitored: number;
}

export function buildCollectionDigestPayload(options: {
  sessions: CollectionSession[];
  posts: Post[];
  stats: DigestStatsShape;
  reportTitle: string;
  jobSummary?: Record<string, unknown> | null;
  jobMeta?: {
    id: string;
    platform: string;
    sources: string[];
    status?: string;
  } | null;
}): OsintPdfDigestPayload {
  const seen = new Set<string>();
  for (const s of options.sessions) {
    for (const p of s.posts) {
      if (p.id) seen.add(p.id);
    }
  }
  const standalone = options.posts.filter((p) => p.id && !seen.has(p.id));

  const sessionsPayload = options.sessions.map((s) => ({
    id: s.id,
    platform: s.platform,
    timestamp: s.timestamp,
    sources: s.sources,
    total_collected: s.total_collected,
    high_risk: s.high_risk,
    medium_risk: s.medium_risk,
    low_risk: s.low_risk,
    posts: s.posts.map(postToPdfJson),
  }));

  const payload: OsintPdfDigestPayload = {
    report_type: 'collection_digest',
    report_title: options.reportTitle,
    report_id: `digest-${Date.now()}`,
    aggregate_stats: { ...options.stats },
    sessions: sessionsPayload,
    standalone_posts: standalone.map(postToPdfJson),
  };

  if (options.jobSummary && Object.keys(options.jobSummary).length > 0) {
    payload.job_summary = options.jobSummary;
  }
  if (options.jobMeta) {
    payload.job_meta = {
      id: options.jobMeta.id,
      platform: options.jobMeta.platform,
      sources: options.jobMeta.sources,
      status: options.jobMeta.status,
    };
  }

  return payload;
}
