// Industry-neutral copy tokens derived from the generated site config.
//
// The section components must never hardcode a vertical's vocabulary (e.g. "patients",
// "smile", "Book Appointment") — that language leaks dental/medical wording onto law,
// accounting and every other kind of business. Instead they read these tokens, which are
// grounded in the config's `audience_noun` and `industry` that the backend derived from the
// client's OWN website.

export interface SiteCopy {
  audience: string;        // clients | patients | customers
  audienceTitle: string;   // Clients | Patients | Customers
  bookLabel: string;       // primary CTA button label
  bookingNoun: string;     // appointment | consultation | visit
  enquireLabel: string;    // short per-service CTA
}

export function siteCopy(config: any): SiteCopy {
  const audience = String(config?.audience_noun || 'clients').toLowerCase();
  const audienceTitle = audience.charAt(0).toUpperCase() + audience.slice(1);
  const industry = String(config?.industry || config?.category || '').toLowerCase();

  const is = (...k: string[]) => k.some((x) => industry.includes(x));

  let bookLabel = 'Get in Touch';
  let bookingNoun = 'enquiry';
  if (is('dent', 'medic', 'clinic', 'health', 'physio', 'optic', 'chiro', 'derm', 'vet', 'spa', 'aesthetic')) {
    bookLabel = 'Book Appointment';
    bookingNoun = 'appointment';
  } else if (is('law', 'legal', 'solicit', 'attorney', 'immigration', 'account', 'cpa', 'tax', 'financ', 'advis', 'consult')) {
    bookLabel = 'Request a Consultation';
    bookingNoun = 'consultation';
  } else if (is('hvac', 'plumb', 'roof', 'electric', 'build', 'contractor', 'repair', 'clean', 'landscap')) {
    bookLabel = 'Get a Free Quote';
    bookingNoun = 'quote';
  }

  const enquireLabel = bookingNoun === 'appointment' ? 'Book' : 'Enquire';
  return { audience, audienceTitle, bookLabel, bookingNoun, enquireLabel };
}
