const fs = require('fs');

// Map of country codes to sources
const sources = {
  'AR': ['Buenos Aires Times'],
  'AU': ['ABC News'],
  'BR': ['Rio Times'],
  'CN': ['CGTN'],
  'DE': ['Deutsche Welle'],
  'DZ': ['TSA'],
  'EG': ['Egypt Independent'],
  'FI': ['Yle News'],
  'FJ': ['FBC News'],
  'FR': ['RFI France'],
  'GB': ['BBC UK'],
  'GH': ['MyJoyOnline'],
  'HK': ['HKFP'],
  'HU': ['Hungary Today'],
  'IE': ['TheJournal'],
  'IL': ['Times of Israel'],
  'IN': ['The Hindu'],
  'IR': ['Tehran Times'],
  'IT': ['ANSA'],
  'JP': ['Japan Times'],
  'KE': ['The Standard'],
  'KR': ['Yonhap'],
  'MX': ['Mexico News Daily'],
  'MY': ['Malay Mail'],
  'NG': ['The Cable'],
  'NL': ['DutchNews'],
  'NP': ['Kathmandu Post'],
  'NZ': ['RNZ', 'Stuff'],
  'PH': ['Rappler'],
  'PK': ['Dawn'],
  'PL': ['Notes from Poland'],
  'PT': ['Portugal News'],
  'RU': ['The Moscow Times'],
  'SE': ['The Local Sweden'],
  'SG': ['Channel News Asia'],
  'TW': ['Taipei Times'],
  'UA': ['The New Voice', 'Ukrinform'],
  'US': ['NPR'],
  'VN': ['VnExpress'],
  'ZW': ['NewZimbabwe'],
};

// Country mapping with labels
const countries = {
  'Europe': [
    { cc: 'GB', label: 'United Kingdom' },
    { cc: 'IE', label: 'Ireland' },
    { cc: 'FR', label: 'France' },
    { cc: 'DE', label: 'Germany' },
    { cc: 'NL', label: 'Netherlands' },
    { cc: 'IT', label: 'Italy' },
    { cc: 'PT', label: 'Portugal' },
    { cc: 'FI', label: 'Finland' },
    { cc: 'SE', label: 'Sweden' },
    { cc: 'DK', label: 'Denmark' },
    { cc: 'PL', label: 'Poland' },
    { cc: 'HU', label: 'Hungary' },
    { cc: 'UA', label: 'Ukraine' },
    { cc: 'RU', label: 'Russia' },
  ],
  'Asia': [
    { cc: 'IN', label: 'India' },
    { cc: 'PK', label: 'Pakistan' },
    { cc: 'BD', label: 'Bangladesh' },
    { cc: 'NP', label: 'Nepal' },
    { cc: 'JP', label: 'Japan' },
    { cc: 'KR', label: 'South Korea' },
    { cc: 'CN', label: 'China' },
    { cc: 'TW', label: 'Taiwan' },
    { cc: 'HK', label: 'Hong Kong' },
    { cc: 'SG', label: 'Singapore' },
    { cc: 'MY', label: 'Malaysia' },
    { cc: 'VN', label: 'Vietnam' },
    { cc: 'PH', label: 'Philippines' },
  ],
  'Middle East': [
    { cc: 'IL', label: 'Israel' },
    { cc: 'IR', label: 'Iran' },
    { cc: 'EG', label: 'Egypt' },
  ],
  'Africa': [
    { cc: 'NG', label: 'Nigeria' },
    { cc: 'KE', label: 'Kenya' },
    { cc: 'GH', label: 'Ghana' },
    { cc: 'ZW', label: 'Zimbabwe' },
  ],
  'Americas': [
    { cc: 'US', label: 'United States' },
    { cc: 'CA', label: 'Canada' },
    { cc: 'MX', label: 'Mexico' },
    { cc: 'BR', label: 'Brazil' },
    { cc: 'AR', label: 'Argentina' },
  ],
  'Oceania': [
    { cc: 'AU', label: 'Australia' },
    { cc: 'NZ', label: 'New Zealand' },
    { cc: 'FJ', label: 'Fiji' },
  ],
  'Other': [
    { cc: 'DZ', label: 'Algeria' },
  ],
};

const SVG_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>';

function buildTree() {
  let html = '';

  for (const [region, countriesList] of Object.entries(countries)) {
    html += `<details class="group" data-region="${region}" open><summary class="group-head"><span class="tri"></span><span class="zdiv"></span><span class="group-name">${region}</span><span class="group-count">${countriesList.length}</span><span class="group-sel"></span></summary><div class="rows">`;

    for (const country of countriesList) {
      const srcs = sources[country.cc] || [];
      const hasSources = srcs.length > 0;

      // Country row with triangle if it has sources
      const triClass = hasSources ? '' : 'style="visibility:hidden"';
      const hasSourcesClass = hasSources ? 'has-sources' : '';
      html += `<div class="country-row ${hasSourcesClass}" data-cc="${country.cc}" data-label="${country.label}" data-sources="${srcs.join('|')}"><span class="tri" ${triClass}></span><span class="zdiv"></span><span class="nm">${country.label}</span><span class="check hidden">${SVG_CHECK}</span></div>`;

      // Source rows
      for (const source of srcs) {
        html += `<div class="source-row" data-cc="${country.cc}" data-source="${source}" style="display:none"><span class="nm">${source}</span><span class="check hidden">${SVG_CHECK}</span></div>`;
      }
    }

    html += `</div></details>`;
  }

  return html;
}

const tree = buildTree();
console.log(tree);
