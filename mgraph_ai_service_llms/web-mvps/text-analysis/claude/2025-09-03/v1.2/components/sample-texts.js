// v1.2/components/sample-texts.js
// Override the sample text functions to always use GDPR as default

// Import the original sample texts
import { SAMPLE_TEXTS, WELCOME_MESSAGES } from '../../../2025-08-22/v1.0/utils/sample-texts.js';

// Export GDPR as the default sample
export function getDefaultSample() {
    return "I want to perform a GDPR Gap analysis and understand what are the risks, and what needs to be addressed";
}

// Keep random for variety if needed later
export function getRandomSample() {
    // For v1.2, always return GDPR sample as default
    return getDefaultSample();
}

// Re-export other functions unchanged
export { getSampleByKey, getSampleKeys, getRandomWelcome, WELCOME_MESSAGES } from '../../../2025-08-22/v1.0/utils/sample-texts.js';