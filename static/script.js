const API = window.location.origin;
let chart = null;
let isLoading = false;
let currentTimeframe = '1y';
let currentSymbol = 'BBRI.JK';
let currentLanguage = localStorage.getItem('language') || 'EN';

let currentCompanyInfo = null;

// ============ LANGUAGE TRANSLATIONS ============
const translations = {
  EN: {
    overview: "Overview",
    chart: "Chart",
    metrics: "Metrics",
    financials: "Financials",
    valuation: "Valuation",
    analysis: "Analysis",
    volume: "Volume",
    marketcap: "Market Cap",
    company_info: "Company Information",
    price_chart: "Price Chart",
    comprehensive_metrics: "Comprehensive Metrics",
    financial_statements: "Financial Statements",
    valuation_analysis: "Valuation Analysis",
    footer: "Educational Purpose | Powered by yfinance © 2026",
    search: "Search",
    price: "Price",
    "1m": "1M",
    "3m": "3M",
    "6m": "6M",
    "1y": "1Y",
    "5y": "5Y",
    "max": "MAX",
    sector: "Sector",
    industry: "Industry",
    website: "Website",
    ceo: "CEO",
    "50d_avg": "50D Average",
    "200d_avg": "200D Average",
    "52w_high": "52W High",
    "52w_low": "52W Low",
    market_cap: "Market Cap",
    pe_ratio: "P/E Ratio",
    pb_ratio: "P/B Ratio",
    ps_ratio: "P/S Ratio",
    forward_pe: "Forward P/E",
    roe: "Return on Equity",
    roa: "Return on Assets",
    profit_margin: "Profit Margin",
    gross_margin: "Gross Margin",
    operating_margin: "Operating Margin",
    der: "Debt-to-Equity Ratio",
    current_ratio: "Current Ratio",
    quick_ratio: "Quick Ratio",
    total_debt: "Total Debt",
    total_equity: "Total Equity",
    total_revenue: "Total Revenue",
    revenue_growth: "Revenue Growth",
    gross_profit: "Gross Profit",
    operating_income: "Operating Income",
    net_income: "Net Income",
    earnings_growth: "Earnings Growth",
    ebitda: "EBITDA",
    total_assets: "Total Assets",
    total_liabilities: "Total Liabilities",
    cash: "Cash",
    operating_cash_flow: "Operating Cash Flow",
    free_cash_flow: "Free Cash Flow",
    dividend_yield: "Dividend Yield",
    eps: "EPS",
    book_value: "Book Value",
    peg_ratio: "PEG Ratio",
    trailing_pe: "Trailing P/E",
    bid: "Bid",
    ask: "Ask",
    avg_volume: "Avg Volume",
    avg_volume_10d: "Avg Volume 10D",
    shares_outstanding: "Shares Outstanding",
    shares_float: "Shares Float",
    dividend_rate: "Dividend Rate",
    payout_ratio: "Payout Ratio",
    target_price: "Target Price",
    recommendation: "Recommendation",
    number_of_analysts: "Number of Analysts",
    ipo_date: "IPO Date",
    beta: "Beta",
    trailing_pe: "Trailing P/E",
    cash_per_share: "Cash Per Share",
    capital_expenditure: "Capital Expenditure",
    relative_valuation: "💹 Relative Valuation",
    dividend_metrics: "🎯 Dividend Metrics",
    risk_metrics: "⚠️ Risk Metrics",
    income_statement: "📈 Income Statement",
    balance_sheet: "📋 Balance Sheet",
    cash_flow: "💵 Cash Flow",
    profitability: "💰 Profitability",
    financial_health: "🏦 Financial Health",
  },
  ID: {
    overview: "Ringkasan",
    chart: "Grafik",
    metrics: "Metrik",
    financials: "Keuangan",
    valuation: "Valuasi",
    analysis: "Analisis",
    volume: "Volume",
    marketcap: "Kapitalisasi Pasar",
    company_info: "Informasi Perusahaan",
    price_chart: "Grafik Harga",
    comprehensive_metrics: "Metrik Komprehensif",
    financial_statements: "Laporan Keuangan",
    valuation_analysis: "Analisis Valuasi",
    footer: "Tujuan Edukatif | Didukung oleh yfinance © 2026",
    search: "Cari",
    price: "Harga",
    "1m": "1B",
    "3m": "3B",
    "6m": "6B",
    "1y": "1T",
    "5y": "5T",
    "max": "MAX",
    trailing_pe: "Historis P/E",
    sector: "Sektor",
    industry: "Industri",
    website: "Website",
    ceo: "CEO",
    "50d_avg": "Rata-rata 50 Hari",
    "200d_avg": "Rata-rata 200 Hari",
    "52w_high": "Tertinggi 52 Minggu",
    "52w_low": "Terendah 52 Minggu",
    market_cap: "Kapitalisasi Pasar",
    pe_ratio: "Rasio P/E",
    pb_ratio: "Rasio P/B",
    ps_ratio: "Rasio P/S",
    forward_pe: "Estimasi P/E",
    roe: "ROE",
    roa: "ROA",
    profit_margin: "Margin Laba",
    gross_margin: "Margin Kotor",
    operating_margin: "Margin Operasi",
    der: "Rasio D/E",
    current_ratio: "Rasio Lancar",
    quick_ratio: "Rasio Cepat",
    total_debt: "Total Utang",
    total_equity: "Total Ekuitas",
    total_revenue: "Total Pendapatan",
    revenue_growth: "Pertumbuhan Pendapatan",
    gross_profit: "Laba Kotor",
    operating_income: "Pendapatan Operasional",
    net_income: "Laba Bersih",
    earnings_growth: "Pertumbuhan Laba",
    ebitda: "EBITDA",
    total_assets: "Total Aset",
    total_liabilities: "Total Kewajiban",
    cash: "Kas",
    operating_cash_flow: "Arus Kas Operasional",
    free_cash_flow: "Arus Kas Bebas",
    dividend_yield: "Hasil Dividen",
    eps: "EPS",
    book_value: "Nilai Buku",
    peg_ratio: "Rasio PEG",
    trailing_pe: "Historis P/E",
    bid: "Bid",
    ask: "Ask",
    avg_volume: "Rata-rata Volume",
    avg_volume_10d: "Rata-rata Volume 10 Hari",
    shares_outstanding: "Saham Beredar",
    shares_float: "Saham Float",
    dividend_rate: "Tingkat Dividen",
    payout_ratio: "Rasio Pembayaran",
    target_price: "Harga Target",
    recommendation: "Rekomendasi",
    number_of_analysts: "Jumlah Analis",
    ipo_date: "Tanggal IPO",
    beta: "Beta",
    cash_per_share: "Kas Per Saham",
    capital_expenditure: "Pengeluaran Modal",
    relative_valuation: "💹 Valuasi Relatif",
    dividend_metrics: "🎯 Metrik Dividen",
    risk_metrics: "⚠️ Metrik Risiko",
    income_statement: "📈 Laporan Laba Rugi",
    balance_sheet: "📋 Neraca",
    cash_flow: "💵 Arus Kas",
    profitability: "💰 Profitabilitas",
    financial_health: "🏦 Kesehatan Keuangan",
  }
};

// ============ SECTOR TRANSLATIONS ============
const sectorTranslations = {
  EN: {
    "Technology": "Technology",
    "Healthcare": "Healthcare",
    "Financials": "Financials",
    "Financial Services": "Financial Services",
    "Consumer Discretionary": "Consumer Discretionary",
    "Consumer Staples": "Consumer Staples",
    "Industrials": "Industrials",
    "Energy": "Energy",
    "Utilities": "Utilities",
    "Real Estate": "Real Estate",
    "Materials": "Materials",
    "Communication Services": "Communication Services",
  },
  ID: {
    "Technology": "Teknologi",
    "Healthcare": "Kesehatan",
    "Financials": "Keuangan",
    "Financial Services": "Layanan Keuangan",
    "Consumer Discretionary": "Konsumen Diskresioner",
    "Consumer Staples": "Konsumen Pokok",
    "Industrials": "Industri",
    "Energy": "Energi",
    "Utilities": "Utilitas",
    "Real Estate": "Real Estat",
    "Materials": "Material",
    "Communication Services": "Layanan Komunikasi",
  }
};

// ============ INDUSTRY TRANSLATIONS ============
const industryTranslations = {
  EN: {
    "Banks - Regional": "Banks - Regional",
    "Regional Banks": "Regional Banks",
    "Regional bank": "Regional bank",
    "Banks": "Banks",
    "Bank": "Bank",
    "Financial Services": "Financial Services",
    "Financial services": "Financial services",
    "Investment Banking": "Investment Banking",
    "Insurance": "Insurance",
    "Asset Management": "Asset Management",
    "Credit Services": "Credit Services",
    "Diversified Financial Services": "Diversified Financial Services",
    "Capital Markets": "Capital Markets",
    "Mortgage Finance": "Mortgage Finance",
    "Software": "Software",
    "Software - Application": "Software - Application",
    "Software - Infrastructure": "Software - Infrastructure",
    "Semiconductors": "Semiconductors",
    "Internet": "Internet",
    "Internet Software & Services": "Internet Software & Services",
    "Hardware": "Hardware",
    "Computer Hardware": "Computer Hardware",
    "Electronics": "Electronics",
    "IT Services": "IT Services",
    "Information Technology Services": "Information Technology Services",
    "Telecom Equipment": "Telecom Equipment",
    "Data Processing Services": "Data Processing Services",
    "Technology Hardware": "Technology Hardware",
    "Computing Hardware": "Computing Hardware",
    "Pharmaceuticals": "Pharmaceuticals",
    "Drugs": "Drugs",
    "Biotechnology": "Biotechnology",
    "Medical Devices": "Medical Devices",
    "Medical Equipment": "Medical Equipment",
    "Hospitals": "Hospitals",
    "Healthcare": "Healthcare",
    "Healthcare Facilities": "Healthcare Facilities",
    "Health Care Services": "Health Care Services",
    "Diagnostic Substances": "Diagnostic Substances",
    "Medical Instruments & Supplies": "Medical Instruments & Supplies",
    "Retail": "Retail",
    "General Merchandise": "General Merchandise",
    "Specialty Retail": "Specialty Retail",
    "Apparel Retail": "Apparel Retail",
    "Department Stores": "Department Stores",
    "Restaurants": "Restaurants",
    "Lodging": "Lodging",
    "Hotels": "Hotels",
    "Casinos & Gaming": "Casinos & Gaming",
    "Leisure": "Leisure",
    "Recreational Services": "Recreational Services",
    "Auto Parts & Equipment": "Auto Parts & Equipment",
    "Automobiles": "Automobiles",
    "Vehicle Manufacturers": "Vehicle Manufacturers",
    "Food Processing": "Food Processing",
    "Beverages": "Beverages",
    "Beverage": "Beverage",
    "Consumer Packaged Goods": "Consumer Packaged Goods",
    "Household & Personal Products": "Household & Personal Products",
    "Food Retail": "Food Retail",
    "Grocery Stores": "Grocery Stores",
    "Packaged Foods": "Packaged Foods",
    "Tobacco": "Tobacco",
    "Agricultural Chemicals": "Agricultural Chemicals",
    "Machinery": "Machinery",
    "Industrial Goods": "Industrial Goods",
    "Electrical Equipment": "Electrical Equipment",
    "Aerospace & Defense": "Aerospace & Defense",
    "Aerospace & defense": "Aerospace & defense",
    "Transportation": "Transportation",
    "Airlines": "Airlines",
    "Railroads": "Railroads",
    "Trucking": "Trucking",
    "Air Freight & Logistics": "Air Freight & Logistics",
    "Marine Transportation": "Marine Transportation",
    "Road & Rail": "Road & Rail",
    "Construction": "Construction",
    "Building Products": "Building Products",
    "Industrial Distribution": "Industrial Distribution",
    "Oil & Gas": "Oil & Gas",
    "Oil & gas": "Oil & gas",
    "Oil & Gas - E&P": "Oil & Gas - E&P",
    "Oil & Gas - Integrated": "Oil & Gas - Integrated",
    "Oil & Gas - Refining & Marketing": "Oil & Gas - Refining & Marketing",
    "Oil & Gas Exploration": "Oil & Gas Exploration",
    "Petroleum": "Petroleum",
    "Coal": "Coal",
    "Utilities": "Utilities",
    "Electric Utilities": "Electric Utilities",
    "Gas Utilities": "Gas Utilities",
    "Water Utilities": "Water Utilities",
    "Renewable Electricity": "Renewable Electricity",
    "Real Estate": "Real Estate",
    "REITs": "REITs",
    "REIT": "REIT",
    "REIT - Industrial": "REIT - Industrial",
    "REIT - Residential": "REIT - Residential",
    "REIT - Office": "REIT - Office",
    "REIT - Retail": "REIT - Retail",
    "REIT - Healthcare": "REIT - Healthcare",
    "REIT - Diversified": "REIT - Diversified",
    "Real Estate Services": "Real Estate Services",
    "Real Estate Operations": "Real Estate Operations",
    "Materials": "Materials",
    "Metals & Mining": "Metals & Mining",
    "Metals and Mining": "Metals and Mining",
    "Chemicals": "Chemicals",
    "Steel": "Steel",
    "Precious Metals & Minerals": "Precious Metals & Minerals",
    "Fertilizers": "Fertilizers",
    "Containers": "Containers",
    "Paper Products": "Paper Products",
    "Lumber & Wood Products": "Lumber & Wood Products",
    "Textiles": "Textiles",
    "Forest Products": "Forest Products",
    "Construction & Engineering": "Construction & Engineering",
    "Building": "Building",
    "Engineering & Construction": "Engineering & Construction",
    "Conglomerates": "Conglomerates",
    "Diversified Industrials": "Diversified Industrials",
    "Infrastructure": "Infrastructure",
    "Telecom Services": "Telecom Services",
    "Telecommunications": "Telecommunications",
    "Wireless Telecom": "Wireless Telecom",
    "Wireline Telecom": "Wireline Telecom",
    "Media": "Media",
    "Publishing": "Publishing",
    "Broadcasting": "Broadcasting",
    "Cable & Satellite": "Cable & Satellite",
    "Entertainment": "Entertainment",
    "Motion Pictures & Entertainment": "Motion Pictures & Entertainment",
  },
  ID: {
    "Banks - Regional": "Bank Daerah",
    "Regional Banks": "Bank Daerah",
    "Regional bank": "Bank Daerah",
    "Banks": "Bank",
    "Bank": "Bank",
    "Financial Services": "Layanan Keuangan",
    "Financial services": "Layanan Keuangan",
    "Investment Banking": "Perbankan Investasi",
    "Insurance": "Asuransi",
    "Asset Management": "Manajemen Aset",
    "Credit Services": "Layanan Kredit",
    "Diversified Financial Services": "Layanan Keuangan Diversifikasi",
    "Capital Markets": "Pasar Modal",
    "Mortgage Finance": "Keuangan Hipotek",
    "Software": "Perangkat Lunak",
    "Software - Application": "Perangkat Lunak - Aplikasi",
    "Software - Infrastructure": "Perangkat Lunak - Infrastruktur",
    "Semiconductors": "Semikonduktor",
    "Internet": "Internet",
    "Internet Software & Services": "Internet Perangkat Lunak & Layanan",
    "Hardware": "Perangkat Keras",
    "Computer Hardware": "Perangkat Keras Komputer",
    "Electronics": "Elektronik",
    "IT Services": "Layanan TI",
    "Information Technology Services": "Layanan Teknologi Informasi",
    "Telecom Equipment": "Peralatan Telekomunikasi",
    "Data Processing Services": "Layanan Pemrosesan Data",
    "Technology Hardware": "Perangkat Keras Teknologi",
    "Computing Hardware": "Perangkat Keras Komputasi",
    "Pharmaceuticals": "Farmasi",
    "Drugs": "Obat-obatan",
    "Biotechnology": "Bioteknologi",
    "Medical Devices": "Perangkat Medis",
    "Medical Equipment": "Peralatan Medis",
    "Hospitals": "Rumah Sakit",
    "Healthcare": "Kesehatan",
    "Healthcare Facilities": "Fasilitas Kesehatan",
    "Health Care Services": "Layanan Perawatan Kesehatan",
    "Diagnostic Substances": "Zat Diagnostik",
    "Medical Instruments & Supplies": "Alat & Perlengkapan Medis",
    "Retail": "Ritel",
    "General Merchandise": "Merchandise Umum",
    "Specialty Retail": "Ritel Khusus",
    "Apparel Retail": "Ritel Pakaian",
    "Department Stores": "Toko Departemen",
    "Restaurants": "Restoran",
    "Lodging": "Penginapan",
    "Hotels": "Hotel",
    "Casinos & Gaming": "Kasino & Permainan",
    "Leisure": "Hiburan",
    "Recreational Services": "Layanan Rekreasi",
    "Auto Parts & Equipment": "Suku Cadang & Peralatan Otomotif",
    "Automobiles": "Otomotif",
    "Vehicle Manufacturers": "Pabrikan Kendaraan",
    "Food Processing": "Pengolahan Makanan",
    "Beverages": "Minuman",
    "Beverage": "Minuman",
    "Consumer Packaged Goods": "Barang Konsumsi Kemasan",
    "Household & Personal Products": "Produk Rumah Tangga & Pribadi",
    "Food Retail": "Ritel Makanan",
    "Grocery Stores": "Toko Kelontong",
    "Packaged Foods": "Makanan Kemasan",
    "Tobacco": "Tembakau",
    "Agricultural Chemicals": "Kimia Pertanian",
    "Machinery": "Mesin",
    "Industrial Goods": "Barang Industri",
    "Electrical Equipment": "Peralatan Listrik",
    "Aerospace & Defense": "Dirgantara & Pertahanan",
    "Aerospace & defense": "Dirgantara & Pertahanan",
    "Transportation": "Transportasi",
    "Airlines": "Maskapai Penerbangan",
    "Railroads": "Kereta Api",
    "Trucking": "Pengangkutan Truk",
    "Air Freight & Logistics": "Kargo Udara & Logistik",
    "Marine Transportation": "Transportasi Laut",
    "Road & Rail": "Jalan & Rel",
    "Construction": "Konstruksi",
    "Building Products": "Produk Bangunan",
    "Industrial Distribution": "Distribusi Industri",
    "Oil & Gas": "Minyak & Gas",
    "Oil & gas": "Minyak & Gas",
    "Oil & Gas - E&P": "Minyak & Gas - Eksplorasi & Produksi",
    "Oil & Gas - Integrated": "Minyak & Gas - Terintegrasi",
    "Oil & Gas - Refining & Marketing": "Minyak & Gas - Penyulingan & Pemasaran",
    "Oil & Gas Exploration": "Eksplorasi Minyak & Gas",
    "Petroleum": "Minyak Bumi",
    "Coal": "Batu Bara",
    "Utilities": "Utilitas",
    "Electric Utilities": "Utilitas Listrik",
    "Gas Utilities": "Utilitas Gas",
    "Water Utilities": "Utilitas Air",
    "Renewable Electricity": "Listrik Terbarukan",
    "Real Estate": "Real Estat",
    "REITs": "REITs",
    "REIT": "REIT",
    "REIT - Industrial": "REIT - Industri",
    "REIT - Residential": "REIT - Perumahan",
    "REIT - Office": "REIT - Perkantoran",
    "REIT - Retail": "REIT - Ritel",
    "REIT - Healthcare": "REIT - Kesehatan",
    "REIT - Diversified": "REIT - Diversifikasi",
    "Real Estate Services": "Layanan Real Estat",
    "Real Estate Operations": "Operasi Real Estat",
    "Materials": "Material",
    "Metals & Mining": "Logam & Pertambangan",
    "Metals and Mining": "Logam dan Pertambangan",
    "Chemicals": "Kimia",
    "Steel": "Baja",
    "Precious Metals & Minerals": "Logam & Mineral Mulia",
    "Fertilizers": "Pupuk",
    "Containers": "Wadah",
    "Paper Products": "Produk Kertas",
    "Lumber & Wood Products": "Kayu Lapis & Produk Kayu",
    "Textiles": "Tekstil",
    "Forest Products": "Produk Hutan",
    "Construction & Engineering": "Konstruksi & Rekayasa",
    "Building": "Bangunan",
    "Engineering & Construction": "Rekayasa & Konstruksi",
    "Conglomerates": "Konglomerat",
    "Diversified Industrials": "Industri Diversifikasi",
    "Infrastructure": "Infrastruktur",
    "Telecom Services": "Layanan Telekomunikasi",
    "Telecommunications": "Telekomunikasi",
    "Wireless Telecom": "Telekomunikasi Nirkabel",
    "Wireline Telecom": "Telekomunikasi Kabel",
    "Media": "Media",
    "Publishing": "Penerbitan",
    "Broadcasting": "Penyiaran",
    "Cable & Satellite": "Kabel & Satelit",
    "Entertainment": "Hiburan",
    "Motion Pictures & Entertainment": "Film & Hiburan",
  }
};

function t(key) {
  if (translations[currentLanguage] && translations[currentLanguage][key]) {
    return translations[currentLanguage][key];
  }
  if (translations['EN'] && translations['EN'][key]) {
    return translations['EN'][key];
  }
  return key;
}

function translateSector(sectorName) {
  if (!sectorName) return "N/A";
  
  if (sectorTranslations[currentLanguage] && sectorTranslations[currentLanguage][sectorName]) {
    return sectorTranslations[currentLanguage][sectorName];
  }
  
  if (sectorTranslations[currentLanguage]) {
    for (const [key, value] of Object.entries(sectorTranslations[currentLanguage])) {
      if (key.toLowerCase() === sectorName.toLowerCase()) {
        return value;
      }
    }
  }
  
  return sectorName;
}

function translateIndustry(industryName) {
  if (!industryName) return "N/A";
  
  if (industryTranslations[currentLanguage] && industryTranslations[currentLanguage][industryName]) {
    return industryTranslations[currentLanguage][industryName];
  }
  
  if (industryTranslations[currentLanguage]) {
    for (const [key, value] of Object.entries(industryTranslations[currentLanguage])) {
      if (key.toLowerCase() === industryName.toLowerCase()) {
        return value;
      }
    }
  }
  
  console.warn(`Industry not found: "${industryName}". Please add it to the mapping.`);
  return industryName;
}

const translationKeyMap = {};
for (const [lang, trans] of Object.entries(translations)) {
  translationKeyMap[lang] = {};
  for (const [key, value] of Object.entries(trans)) {
    const cleanValue = value.replace(/[💹🎯⚠️📈📋💵💰🏦]/g, '').trim();
    translationKeyMap[lang][cleanValue] = key;
  }
}

function updateLanguage() {
  document.querySelectorAll('[data-label]').forEach(el => {
    const key = el.dataset.label;
    const text = t(key);
    
    if (el.tagName === 'INPUT') {
      el.placeholder = text;
    } else if (el.tagName === 'BUTTON' && el.id !== 'lang-btn' && el.id !== 'theme-btn') {
      el.textContent = text;
    } else if (el.tagName === 'SPAN' || el.tagName === 'H3' || el.tagName === 'P') {
      el.textContent = text;
    }
  });
  
  const metricsGrid = document.getElementById('metrics-grid');
  const financialsGrid = document.getElementById('financials-grid');
  const valuationGrid = document.getElementById('valuation-grid');
  const companyInfoGrid = document.getElementById('company-info');
  
  if (metricsGrid && metricsGrid.innerHTML) updateGridTranslations(metricsGrid);
  if (financialsGrid && financialsGrid.innerHTML) updateGridTranslations(financialsGrid);
  if (valuationGrid && valuationGrid.innerHTML) updateGridTranslations(valuationGrid);
  
  if (companyInfoGrid && companyInfoGrid.innerHTML && currentCompanyInfo) {
    renderCompanyInfo(currentCompanyInfo);
  }

  if (chart) updateChartLanguage();
  updateLanguageButton();
}

function updateGridTranslations(grid) {
  const labels = grid.querySelectorAll('.info-label');
  const groupTitles = grid.querySelectorAll('.metrics-group-title');
  
  labels.forEach(label => {
    const key = findKeyFromAnyLanguage(label.textContent);
    if (key) label.textContent = t(key);
  });
  
  groupTitles.forEach(title => {
    const cleanText = title.textContent.replace(/[💹🎯⚠️📈📋💵💰🏦]/g, '').trim();
    const key = findKeyFromAnyLanguage(cleanText);
    if (key) title.textContent = t(key);
  });
}

function findKeyFromAnyLanguage(value) {
  const cleanValue = value.replace(/[💹🎯⚠️📈📋💵💰🏦]/g, '').trim();
  for (const [lang, keyMap] of Object.entries(translationKeyMap)) {
    if (keyMap[cleanValue]) return keyMap[cleanValue];
  }
  for (const [key, val] of Object.entries(translations['EN'])) {
    const cleanVal = val.replace(/[💹🎯⚠️📈📋💵💰🏦]/g, '').trim();
    if (cleanVal === cleanValue) return key;
  }
  return null;
}

function updateChartTheme() {
  if (!chart) return;
  const isDarkTheme = document.body.classList.contains("dark");
  const textColor = isDarkTheme ? "#f1f5f9" : "#0f172a";
  const gridColor = isDarkTheme ? "#94a3b8" : "#64748b";
  
  chart.options.plugins.legend.labels.color = textColor;
  chart.options.scales.x.ticks.color = gridColor;
  chart.options.scales.y.ticks.color = gridColor;
  chart.options.scales.y.grid.color = isDarkTheme ? "rgba(148, 163, 184, 0.1)" : "rgba(148, 163, 184, 0.2)";
  chart.update();
}

function updateChartLanguage() {
  if (!chart || !chart.data.datasets[0]) return;
  chart.data.datasets[0].label = t('price');
  updateChartTheme();
  chart.update();
}

// ============ THEME ============
const themeBtn = document.getElementById("theme-btn");
const langBtn = document.getElementById("lang-btn");

function initTheme() {
  const savedTheme = localStorage.getItem("theme") || "dark";
  document.body.classList.add(savedTheme);
  updateThemeIcon();
}

function updateThemeIcon() {
  const isDark = document.body.classList.contains("dark");
  themeBtn.textContent = isDark ? "🌙" : "☀️";
}

function updateLanguageButton() {
  langBtn.textContent = `🌐 ${currentLanguage}`;
}

themeBtn.addEventListener("click", () => {
  document.body.classList.toggle("light");
  document.body.classList.toggle("dark");
  updateThemeIcon();
  localStorage.setItem("theme", document.body.classList.contains("dark") ? "dark" : "light");
  rippleEffect(event);
  if (chart) updateChartTheme();
});

langBtn.addEventListener("click", () => {
  currentLanguage = currentLanguage === 'EN' ? 'ID' : 'EN';
  localStorage.setItem('language', currentLanguage);
  updateLanguage();
  rippleEffect(event);
});

// ============ RIPPLE EFFECT ============
function rippleEffect(e) {
  if (!e || !e.target) return;
  const btn = e.target;
  const rect = btn.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const ripple = document.createElement("span");
  ripple.style.width = "20px";
  ripple.style.height = "20px";
  ripple.style.background = "rgba(255,255,255,0.5)";
  ripple.style.position = "absolute";
  ripple.style.borderRadius = "50%";
  ripple.style.left = x + "px";
  ripple.style.top = y + "px";
  ripple.style.pointerEvents = "none";
  ripple.style.animation = "ripple 0.6s ease-out";
  btn.style.position = "relative";
  btn.style.overflow = "hidden";
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);
}

const style = document.createElement("style");
style.textContent = `@keyframes ripple { from { transform: scale(0); opacity: 1; } to { transform: scale(4); opacity: 0; } }`;
document.head.appendChild(style);

// ============ SEARCH ============
document.getElementById("search-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const symbol = document.getElementById("symbol").value.toUpperCase().trim();
  if (symbol) { currentSymbol = symbol; loadData(symbol); }
});

document.getElementById("symbol").addEventListener("focus", (e) => {
  e.target.style.transform = "scale(1.02)";
});

document.getElementById("symbol").addEventListener("blur", (e) => {
  e.target.style.transform = "scale(1)";
});

// ============ TABS ============
function showTab(name) {
  const allTabs = document.querySelectorAll(".tab-content");
  const allBtns = document.querySelectorAll(".tab-btn");
  allTabs.forEach((tab) => { tab.classList.remove("active"); tab.style.pointerEvents = "none"; });
  allBtns.forEach((btn) => btn.classList.remove("active"));
  
  const targetTab = document.getElementById(name);
  if (targetTab) { targetTab.classList.add("active"); targetTab.style.pointerEvents = "auto"; }
  if (event && event.target) {
    event.target.classList.add("active");
    event.target.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  }
}

// ============ TIMEFRAME SELECTOR ============
function setTimeframe(timeframe, symbol) {
  currentTimeframe = timeframe;
  document.querySelectorAll(".timeframe-btn").forEach(btn => btn.classList.remove("active"));
  if (event && event.target) {
    event.target.classList.add("active");
    loadChartData(symbol || currentSymbol, timeframe);
  }
}

function formatChartDateRange(timeframe, data) {
  if (!data || !data.dates || data.dates.length === 0) return timeframe;
  const firstDate = data.dates[0];
  const lastDate = data.dates[data.dates.length - 1];
  if (timeframe === 'max' || timeframe === '5y') {
    return `${firstDate} - ${lastDate}`;
  } else {
    const currentDate = new Date();
    const year = currentDate.getFullYear();
    return `${firstDate} - ${lastDate} (${year})`;
  }
}

// ============ TOAST ============
function toast(msg, type = "error") {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = msg;
  el.className = `toast show`;
  if (type === "success") {
    el.style.background = "linear-gradient(135deg, var(--success) 0%, rgba(55, 214, 122, 0.8) 100%)";
  } else {
    el.style.background = "linear-gradient(135deg, var(--danger) 0%, rgba(237, 69, 90, 0.8) 100%)";
  }
  setTimeout(() => { el.classList.remove("show"); }, 3000);
}

// ============ LOADING ============
function showLoading() {
  isLoading = true;
  ["name", "price", "change", "volume", "marketcap"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) { el.style.opacity = "0.5"; el.style.animation = "pulse 1.5s infinite"; }
  });
}

function hideLoading() {
  isLoading = false;
  ["name", "price", "change", "volume", "marketcap"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) { el.style.opacity = "1"; el.style.animation = ""; }
  });
}

const pulseStyle = document.createElement("style");
pulseStyle.textContent = `@keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 0.8; } }`;
document.head.appendChild(pulseStyle);

// ============ LOAD DATA ============
async function loadData(symbol) {
  if (isLoading) return;
  showLoading();

  try {
    // Load sequentially with delays to avoid rate limiting
    const stock = await fetch(`${API}/api/stock/${symbol}`).then((r) => r.json());
    if (stock.error) { toast(`❌ ${stock.error}`); hideLoading(); return; }
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    const chartData = await fetch(`${API}/api/chart-extended/${symbol}/1y`).then((r) => r.json());
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    const info = await fetch(`${API}/api/info/${symbol}`).then((r) => r.json());
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    const metrics = await fetch(`${API}/api/metrics/${symbol}`).then((r) => r.json());
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    const financials = await fetch(`${API}/api/financials/${symbol}`).then((r) => r.json());
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    const valuation = await fetch(`${API}/api/valuation/${symbol}`).then((r) => r.json());

    setTimeout(() => {
      renderStockData(stock);
      if (!chartData.error) renderChartData(chartData);
      if (!info.error) { currentCompanyInfo = info; renderCompanyInfo(info); }
      if (!metrics.error) renderMetrics(metrics);
      if (!financials.error) renderFinancials(financials);
      if (!valuation.error) renderValuation(valuation);
      hideLoading();
      toast(`✅ ${stock.name} loaded successfully!`, "success");
    }, 300);
  } catch (error) {
    console.error("Error loading data:", error);
    toast("❌ Error loading data");
    hideLoading();
  }
}

async function loadChartData(symbol, timeframe) {
  try {
    const chartData = await fetch(`${API}/api/chart-extended/${symbol}/${timeframe}`).then((r) => r.json());
    if (!chartData.error && chartData.closes) {
      renderChartData(chartData);
    } else {
      toast(`⚠️ Chart data unavailable`);
    }
  } catch (error) {
    console.error("Error loading chart data:", error);
    toast("❌ Error loading chart data");
  }
}

// ============ RENDER FUNCTIONS ============
function renderStockData(stock) {
  const nameEl = document.getElementById("name");
  const priceEl = document.getElementById("price");
  const changeEl = document.getElementById("change");
  const volumeEl = document.getElementById("volume");
  const capEl = document.getElementById("marketcap");

  if (nameEl) {
    nameEl.style.opacity = "0";
    nameEl.textContent = `${stock.name} (${stock.symbol})`;
    nameEl.style.animation = "fadeInDown 0.6s ease-out forwards";
  }

  if (priceEl) {
    priceEl.style.opacity = "0";
    priceEl.textContent = stock.price.toLocaleString("id-ID");
    priceEl.style.animation = "slideInPrice 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards";
  }

  if (changeEl) {
    changeEl.style.opacity = "0";
    const isUp = stock.status === "up";
    changeEl.textContent = `${isUp ? "📈" : "📉"} ${Math.abs(stock.change)} (${Math.abs(stock.change_pct).toFixed(2)}%)`;
    changeEl.className = `change ${isUp ? "up" : "down"}`;
    changeEl.style.animation = "bounceIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.2s forwards";
  }

  if (volumeEl) {
    volumeEl.textContent = stock.volume.toLocaleString("id-ID");
    if (volumeEl.parentElement && volumeEl.parentElement.parentElement) {
      volumeEl.parentElement.parentElement.style.animation = "slideInInfoItem 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s both";
    }
  }

  if (capEl) {
    capEl.textContent = typeof stock.marketcap === "number" ? (stock.marketcap / 1e9).toFixed(2) + "B" : stock.marketcap;
    if (capEl.parentElement && capEl.parentElement.parentElement) {
      capEl.parentElement.parentElement.style.animation = "slideInInfoItem 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.4s both";
    }
  }
}

function renderChartData(chartData) {
  const canvas = document.getElementById("myChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  if (chart) chart.destroy();

  const dateRangeEl = document.getElementById("chart-date-range");
  if (dateRangeEl) {
    dateRangeEl.style.opacity = "0";
    dateRangeEl.style.transform = "translateX(-20px)";
    dateRangeEl.style.transition = "all 0.4s ease";
    dateRangeEl.textContent = formatChartDateRange(currentTimeframe, chartData);
    setTimeout(() => {
      dateRangeEl.style.opacity = "1";
      dateRangeEl.style.transform = "translateX(0)";
    }, 100);
  }

  const isUp = chartData.closes[chartData.closes.length - 1] >= chartData.closes[0];
  const colors = { 
    border: isUp ? "#37d67a" : "#ed455a", 
    bg: isUp ? "rgba(55, 214, 122, 0.1)" : "rgba(237, 69, 90, 0.1)" 
  };

  const isDarkTheme = document.body.classList.contains("dark");
  const textColor = isDarkTheme ? "#f1f5f9" : "#0f172a";
  const gridColor = isDarkTheme ? "#94a3b8" : "#64748b";

  canvas.style.transition = "none";
  canvas.style.opacity = "1";
  canvas.style.transform = "scale(1) translateY(0)";
  
  void canvas.offsetWidth;
  
  canvas.style.opacity = "0";
  canvas.style.transform = "scale(0.95) translateY(20px)";
  canvas.style.transition = "opacity 0.7s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.7s cubic-bezier(0.34, 1.56, 0.64, 1)";

  try {
    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: chartData.dates || [],
        datasets: [{
          label: t('price'),
          data: chartData.closes || [],
          borderColor: colors.border,
          backgroundColor: colors.bg,
          borderWidth: 3,
          tension: 0.4,
          fill: true,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: colors.border,
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointHoverBorderWidth: 3,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        interaction: { mode: "index", intersect: false },
        animation: {
          duration: 1500,
          easing: "easeInOutQuart",
          delay: (context) => {
            let delay = 0;
            if (context.type === 'data') {
              delay = context.dataIndex * 20 + context.datasetIndex * 100;
            }
            return delay;
          },
          onComplete: () => {
            setTimeout(() => {
              canvas.style.opacity = "1";
              canvas.style.transform = "scale(1) translateY(0)";
            }, 200);
          }
        },
        plugins: {
          legend: {
            display: true,
            labels: { 
              usePointStyle: true, 
              padding: 20, 
              font: { size: 12, weight: 600 }, 
              color: textColor 
            },
          },
          tooltip: {
            enabled: true,
            mode: "index",
            intersect: false,
            backgroundColor: "rgba(0, 0, 0, 0.9)",
            borderColor: colors.border,
            borderWidth: 2,
            titleFont: { size: 13, weight: 600 },
            bodyFont: { size: 12 },
            padding: 12,
            displayColors: true,
            borderRadius: 8,
            titleColor: textColor,
            bodyColor: textColor,
            animation: {
              duration: 300,
              easing: "easeInOutQuart"
            },
            callbacks: {
              label: (context) => {
                return `${t('price')}: ${context.parsed.y.toLocaleString("id-ID")}`;
              },
            },
          },
        },
        scales: {
          x: { 
            display: true, 
            grid: { display: false, drawBorder: true }, 
            ticks: { color: gridColor, font: { size: 11, weight: 500 } } 
          },
          y: {
            beginAtZero: false,
            grid: { color: isDarkTheme ? "rgba(148, 163, 184, 0.1)" : "rgba(148, 163, 184, 0.2)", drawBorder: true },
            ticks: { color: gridColor, font: { size: 11, weight: 500 }, callback: (value) => value.toLocaleString("id-ID") },
          },
        },
      },
    });
  } catch (error) {
    console.error("Error rendering chart:", error);
  }
}

function renderCompanyInfo(info) {
  const items = [
    { label: "sector", value: info.sector ? translateSector(info.sector) : "N/A" },
    { label: "industry", value: info.industry ? translateIndustry(info.industry) : "N/A" },
    { label: "website", value: info.website || "N/A" },
    { label: "ceo", value: info.ceo || "N/A" },
  ];

  const grid = document.getElementById("company-info");
  if (!grid) return;
  grid.innerHTML = "";

  items.forEach((item, index) => {
    const el = document.createElement("div");
    el.className = "info-item";
    el.style.animation = `slideInInfoItem 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) ${index * 0.05}s forwards`;

    const label = document.createElement("span");
    label.className = "info-label";
    label.textContent = t(item.label);

    const value = document.createElement("span");
    value.className = "info-value";
    value.textContent = formatValue(item.value);

    el.appendChild(label);
    el.appendChild(value);
    grid.appendChild(el);
  });
}

function renderMetrics(metrics) {
  const groups = [
    {
      title: t("relative_valuation"),
      items: Object.entries(metrics.valuation || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    },
    {
      title: t("profitability"),
      items: Object.entries(metrics.profitability || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    },
    {
      title: t("financial_health"),
      items: Object.entries(metrics.financial_health || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    }
  ];

  renderGroupedMetrics("metrics-grid", groups);
}

function renderFinancials(financials) {
  const groups = [
    {
      title: t("income_statement"),
      items: Object.entries(financials.income_statement || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    },
    {
      title: t("balance_sheet"),
      items: Object.entries(financials.balance_sheet || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    },
    {
      title: t("cash_flow"),
      items: Object.entries(financials.cash_flow || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    }
  ];

  renderGroupedMetrics("financials-grid", groups);
}

function renderValuation(valuation) {
  const groups = [
    {
      title: t("relative_valuation"),
      items: Object.entries(valuation.relative_valuation || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    },
    {
      title: t("dividend_metrics"),
      items: Object.entries(valuation.dividend_metrics || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    },
    {
      title: t("risk_metrics"),
      items: Object.entries(valuation.risk_metrics || {})
        .filter(([_, value]) => value !== 'N/A')
        .map(([key, value]) => ({ label: t(key), value: value, unit: getUnit(key, value) }))
    }
  ];

  renderGroupedMetrics("valuation-grid", groups);
}

function renderGroupedMetrics(gridId, groups) {
  const grid = document.getElementById(gridId);
  if (!grid) return;
  grid.innerHTML = "";

  groups.forEach((group, groupIndex) => {
    if (group.items.length === 0) return;

    const groupDiv = document.createElement("div");
    groupDiv.className = "metrics-group";
    groupDiv.style.animation = `fadeInUp 0.6s ease-out ${groupIndex * 0.1}s both`;

    const title = document.createElement("h4");
    title.textContent = group.title;
    title.className = "metrics-group-title";
    groupDiv.appendChild(title);

    const metricsContainer = document.createElement("div");
    metricsContainer.className = "metrics-container";

    group.items.forEach((item, index) => {
      const el = document.createElement("div");
      el.className = "info-item";
      el.style.animation = `slideInInfoItem 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) ${groupIndex * 0.1 + index * 0.05}s forwards`;

      const label = document.createElement("span");
      label.className = "info-label";
      label.textContent = item.label;

      const value = document.createElement("span");
      value.className = "info-value";
      value.textContent = formatValueWithUnit(item.value, item.unit);

      el.appendChild(label);
      el.appendChild(value);
      metricsContainer.appendChild(el);
    });

    groupDiv.appendChild(metricsContainer);
    grid.appendChild(groupDiv);
  });
}

function getUnit(key, value) {
  const percentageKeys = ['profit_margin', 'gross_margin', 'operating_margin', 'dividend_yield', 'revenue_growth', 'earnings_growth', 'roe', 'roa'];
  if (percentageKeys.includes(key)) return '%';
  
  const largeValueKeys = ['total_revenue', 'gross_profit', 'operating_income', 'net_income', 'ebitda', 'total_assets', 'total_liabilities', 'total_equity', 'total_debt', 'cash', 'operating_cash_flow', 'free_cash_flow'];
  if (largeValueKeys.includes(key)) {
    if (typeof value === 'number' && Math.abs(value) >= 1e9) return 'B';
    if (typeof value === 'number' && Math.abs(value) >= 1e6) return 'M';
    return '';
  }
  return '';
}

function formatValueWithUnit(value, unit) {
  if (value === "N/A" || !value) return "N/A";
  let formatted = "";
  if (typeof value === "number") {
    if (unit === '%') {
      formatted = value.toFixed(2) + '%';
    } else if (unit === 'B') {
      formatted = (value / 1e9).toFixed(2) + ' B';
    } else if (unit === 'M') {
      formatted = (value / 1e6).toFixed(2) + ' M';
    } else {
      if (Math.abs(value) >= 1e9) {
        formatted = (value / 1e9).toFixed(2) + ' B';
      } else if (Math.abs(value) >= 1e6) {
        formatted = (value / 1e6).toFixed(2) + ' M';
      } else if (Math.abs(value) >= 1e3) {
        formatted = (value / 1e3).toFixed(2) + ' K';
      } else if (Math.abs(value) < 1 && value !== 0) {
        formatted = value.toFixed(4);
      } else {
        formatted = value.toFixed(2);
      }
    }
  }
  return formatted;
}

function formatValue(value) {
  if (value === "N/A" || !value) return "N/A";
  if (typeof value === "number") {
    if (Math.abs(value) >= 1e9) return (value / 1e9).toFixed(2) + "B";
    else if (Math.abs(value) >= 1e6) return (value / 1e6).toFixed(2) + "M";
    else if (Math.abs(value) >= 1e3) return (value / 1e3).toFixed(2) + "K";
    else if (Math.abs(value) < 1 && value !== 0) return value.toFixed(4);
    else return value.toFixed(2);
  }
  if (typeof value === "string") return value;
  return String(value);
}

// ============ INIT ============
window.addEventListener("load", () => {
  initTheme();
  updateLanguageButton();
  updateLanguage();

  document.querySelectorAll("nav, .container, footer").forEach((el, index) => {
    el.style.animation = `fadeInUp 0.6s ease-out ${0.1 * index}s both`;
  });

  const timeframeButtons = document.querySelectorAll(".timeframe-btn");
  timeframeButtons.forEach((btn, index) => {
    if (index === 3) btn.classList.add("active");
  });

  loadData("BBRI.JK");
});

// ============ KEYBOARD SHORTCUTS ============
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault();
    const symbolInput = document.getElementById("symbol");
    if (symbolInput) { symbolInput.focus(); symbolInput.select(); }
  }
});

window.addEventListener("load", () => {
  document.body.style.opacity = "0";
  setTimeout(() => {
    document.body.style.opacity = "1";
    document.body.style.transition = "opacity 0.5s ease-out";
  }, 100);
});