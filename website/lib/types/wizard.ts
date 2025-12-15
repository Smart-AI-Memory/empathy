/**
 * Wizard type definitions for the website
 */

export interface Wizard {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'software' | 'healthcare' | 'coach' | 'domain';
  subcategory: string;
  distributions: ('open_source' | 'enterprise' | 'healthcare')[];
  empathyLevel: 1 | 2 | 3 | 4 | 5;
  redis: 'none' | 'optional' | 'recommended' | 'required';
  compliance: string[];
  features: string[];
  demoReady: boolean;
  blogFeatured: boolean;
  websiteFeatured: boolean;
}
