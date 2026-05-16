#!/usr/bin/env node
const fs = require('fs');

const DATA_FILES = [
  { path: 'data/events.json', type: 'events' },
  { path: 'data/spots.json', type: 'spots' },
  { path: 'data/outdoor.json', type: 'outdoor' },
  { path: 'data/hotels.json', type: 'hotels' },
  { path: 'data/products.json', type: 'products' }
];

function loadJson(path, fallback) {
  if (!fs.existsSync(path)) return fallback;
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function isOfficialUrl(url) {
  return /^https:\/\//.test(String(url || ''));
}

function normalizeCommon(item) {
  return {
    ...item,
    dogPolicy: item.dogPolicy || '要確認',
    largeDogFriendly: typeof item.largeDogFriendly === 'boolean' ? item.largeDogFriendly : '要確認',
    indoorOk: typeof item.indoorOk === 'boolean' ? item.indoorOk : '要確認',
    rainyDayOk: typeof item.rainyDayOk === 'boolean' ? item.rainyDayOk : '要確認'
  };
}

function isFutureOrOngoingEvent(item) {
  const d = String(item.date || '');
  if (!d) return false;
  if (/(通年|要確認|春|夏|秋|冬|おすすめ)/.test(d)) return true;
  const m = d.match(/(\d{4})\/(\d{1,2})\/(\d{1,2})/);
  if (!m) return true;
  const y = Number(m[1]);
  const mo = Number(m[2]);
  const da = Number(m[3]);
  const t = new Date(Date.UTC(y, mo - 1, da + 1));
  const now = new Date();
  return t >= new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
}

for (const f of DATA_FILES) {
  if (!fs.existsSync(f.path)) {
    console.log(`skip: ${f.path} (not found)`);
    continue;
  }

  const records = loadJson(f.path, []);
  if (!Array.isArray(records)) {
    throw new Error(`${f.path} is not an array JSON`);
  }

  let normalized = records.map(normalizeCommon).filter((x) => isOfficialUrl(x.url));

  if (f.type === 'events') {
    normalized = normalized.filter(isFutureOrOngoingEvent);
  }

  fs.writeFileSync(f.path, JSON.stringify(normalized, null, 2) + '\n');
  console.log(`updated: ${f.path} (${normalized.length} records)`);
}
