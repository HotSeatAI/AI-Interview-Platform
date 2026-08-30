// Countries list plus a curated set of major cities per country, used to
// power the dependent Country -> City dropdowns on the complete-profile
// page. Both fields are optional, so a country with no curated city list
// still lets the user type their city freely instead of being blocked.

export const COUNTRIES = [
  "Afghanistan", "Albania", "Algeria", "Argentina", "Armenia", "Australia",
  "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Belarus", "Belgium",
  "Bolivia", "Bosnia and Herzegovina", "Brazil", "Bulgaria", "Cambodia",
  "Cameroon", "Canada", "Chile", "China", "Colombia", "Costa Rica",
  "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark",
  "Dominican Republic", "Ecuador", "Egypt", "Estonia", "Ethiopia",
  "Finland", "France", "Georgia", "Germany", "Ghana", "Greece",
  "Guatemala", "Honduras", "Hong Kong", "Hungary", "Iceland", "India",
  "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica",
  "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait", "Latvia", "Lebanon",
  "Lithuania", "Luxembourg", "Malaysia", "Malta", "Mexico", "Mongolia",
  "Morocco", "Myanmar", "Nepal", "Netherlands", "New Zealand", "Nigeria",
  "North Macedonia", "Norway", "Oman", "Pakistan", "Panama", "Paraguay",
  "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania",
  "Russia", "Rwanda", "Saudi Arabia", "Serbia", "Singapore", "Slovakia",
  "Slovenia", "South Africa", "South Korea", "Spain", "Sri Lanka",
  "Sudan", "Sweden", "Switzerland", "Taiwan", "Tanzania", "Thailand",
  "Tunisia", "Turkey", "Uganda", "Ukraine", "United Arab Emirates",
  "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Venezuela",
  "Vietnam", "Zimbabwe", "Other",
];

export const CITIES_BY_COUNTRY = {
  India: [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Ahmedabad", "Chennai",
    "Kolkata", "Pune", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur",
    "Indore", "Thane", "Bhopal", "Visakhapatnam", "Vadodara", "Ghaziabad",
    "Coimbatore", "Chandigarh", "Gurugram", "Noida", "Kochi",
  ],
  "United States": [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "San Francisco", "Seattle", "Boston", "Denver",
    "Washington", "Atlanta", "Miami", "Portland", "Detroit",
  ],
  "United Kingdom": [
    "London", "Birmingham", "Manchester", "Glasgow", "Liverpool",
    "Leeds", "Sheffield", "Bristol", "Edinburgh", "Cardiff", "Belfast",
    "Newcastle", "Nottingham", "Oxford", "Cambridge",
  ],
  Canada: [
    "Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa",
    "Winnipeg", "Quebec City", "Hamilton", "Halifax",
  ],
  Australia: [
    "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra",
    "Gold Coast", "Hobart", "Darwin",
  ],
  Germany: [
    "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart",
    "Dusseldorf", "Leipzig", "Dortmund", "Essen",
  ],
  France: [
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes",
    "Strasbourg", "Bordeaux", "Lille",
  ],
  Singapore: ["Singapore"],
  "United Arab Emirates": [
    "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Al Ain", "Ras Al Khaimah",
  ],
  China: [
    "Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Chengdu", "Wuhan",
    "Hangzhou", "Nanjing", "Xian", "Tianjin",
  ],
  Japan: [
    "Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo", "Kobe", "Kyoto",
    "Fukuoka",
  ],
  "South Korea": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju"],
  Brazil: [
    "Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador", "Fortaleza",
    "Belo Horizonte", "Curitiba", "Recife",
  ],
  Netherlands: [
    "Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven",
  ],
  Ireland: ["Dublin", "Cork", "Limerick", "Galway"],
  Switzerland: ["Zurich", "Geneva", "Basel", "Bern", "Lausanne"],
  Spain: ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao", "Malaga"],
  Italy: ["Rome", "Milan", "Naples", "Turin", "Florence", "Bologna"],
  Mexico: [
    "Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana",
  ],
  Indonesia: [
    "Jakarta", "Surabaya", "Bandung", "Medan", "Semarang",
  ],
  Philippines: ["Manila", "Quezon City", "Davao City", "Cebu City"],
  Malaysia: ["Kuala Lumpur", "George Town", "Johor Bahru", "Ipoh"],
  Vietnam: ["Ho Chi Minh City", "Hanoi", "Da Nang", "Can Tho"],
  Thailand: ["Bangkok", "Chiang Mai", "Pattaya", "Phuket"],
  "Saudi Arabia": ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam"],
  "New Zealand": ["Auckland", "Wellington", "Christchurch", "Hamilton"],
  Pakistan: ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad"],
  Bangladesh: ["Dhaka", "Chittagong", "Khulna", "Rajshahi"],
  Nigeria: ["Lagos", "Abuja", "Kano", "Ibadan"],
  "South Africa": [
    "Johannesburg", "Cape Town", "Durban", "Pretoria",
  ],
  Egypt: ["Cairo", "Alexandria", "Giza", "Shubra El Kheima"],
  Turkey: ["Istanbul", "Ankara", "Izmir", "Bursa"],
  Poland: ["Warsaw", "Krakow", "Lodz", "Wroclaw"],
  Sweden: ["Stockholm", "Gothenburg", "Malmo"],
  Norway: ["Oslo", "Bergen", "Trondheim"],
  Denmark: ["Copenhagen", "Aarhus", "Odense"],
  Finland: ["Helsinki", "Espoo", "Tampere"],
  Israel: ["Tel Aviv", "Jerusalem", "Haifa"],
  Russia: ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg"],
  "Hong Kong": ["Hong Kong"],
  Taiwan: ["Taipei", "Kaohsiung", "Taichung"],
};

// Reverse lookup (lowercased city name -> country, plus the canonical
// city spelling) so picking/typing a city with no country selected yet
// can fill in the country automatically. Cities that exist under more
// than one country (e.g. "Hamilton" in both Canada and New Zealand)
// are left out - better to leave the country blank than guess wrong.
const cityLookupCounts = {};
for (const cities of Object.values(CITIES_BY_COUNTRY)) {
  for (const city of cities) {
    const key = city.toLowerCase();
    cityLookupCounts[key] = (cityLookupCounts[key] || 0) + 1;
  }
}

export const CITY_TO_COUNTRY = {};
for (const [country, cities] of Object.entries(CITIES_BY_COUNTRY)) {
  for (const city of cities) {
    const key = city.toLowerCase();
    if (cityLookupCounts[key] === 1) {
      CITY_TO_COUNTRY[key] = { country, city };
    }
  }
}
