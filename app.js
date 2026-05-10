async function loadItems() {
  const res = await fetch('./data/events.json', { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

const esc = (s='') => String(s).replace(/[&<>'"]/g, m => ({
  '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'
}[m]));

const safeUrl = (u='') => /^https:\/\//.test(String(u)) ? String(u) : '';
const safeImg = (u='') => /^https:\/\//.test(String(u)) ? String(u) : '';

function cardImage(i){
  const src = safeImg(i.imageUrl || '');
  return src ? `<img class="card-img" src="${src}" alt="${esc(i.title)}" loading="lazy">` : '';
}

function renderApp(items){
  const updated = document.getElementById('lastUpdated');
  const latest = items.map(i => i.updatedAt).filter(Boolean).sort().pop();
  if (updated && latest) updated.textContent = `最終更新: ${latest.replace('T',' ').replace('Z',' UTC')}`;

  // 公開は承認済みのみ
  const publicItems = items.filter(i => (i.status || '') === '公式確認済み');

  const q = document.getElementById('q');
  const pref = document.getElementById('pref');
  const cat = document.getElementById('cat');
  const season = document.getElementById('season');
  const largeDog = document.getElementById('largeDog');
  const quick = document.getElementById('quick');

  const prefs = ['すべて', ...new Set(publicItems.map(i => i.prefecture))];
  const cats = ['すべて', ...new Set(publicItems.map(i => i.category))];

  pref.innerHTML = ''; cat.innerHTML = '';
  prefs.forEach(v => pref.add(new Option(v, v)));
  cats.forEach(v => cat.add(new Option(v, v)));

  function render(){
    const kw = q.value.trim().toLowerCase();
    const filtered = publicItems.filter(i =>
      (!kw || `${i.title} ${i.summary}`.toLowerCase().includes(kw)) &&
      (pref.value === 'すべて' || i.prefecture === pref.value) &&
      (cat.value === 'すべて' || i.category === cat.value) &&
      ((season?.value || 'すべて') === 'すべて' || (i.seasons || []).includes(season.value))
    ).sort((a,b) => {
      const f = String(b.updatedAt||'').localeCompare(String(a.updatedAt||''));
      if (f !== 0) return f;
      return largeDog?.checked ? (b.largeDogFriendly===true)-(a.largeDogFriendly===true) : 0;
    });

    document.getElementById('count').textContent = `${filtered.length} 件`;

    document.getElementById('list').innerHTML = filtered.map(i => `
      <article class="card">
        ${cardImage(i)}
        <div class="badges">
          <span class="badge">${esc(i.status || '要確認')}</span>
          <span class="badge">${esc(i.category)}</span>
        </div>
        <h3>${esc(i.title)}</h3>
        <p class="sub">${esc(i.prefecture)}・${esc(i.area)} / ${esc(i.date)}</p>
        <p>${esc(i.summary)}</p>

        <div class="actions">
          ${safeUrl(i.url) ? `<a class="btn btn-main" href="${safeUrl(i.url)}" target="_blank" rel="noreferrer">公式サイトを見る</a>` : '<span class="sub">公式確認中</span>'}
          ${safeUrl(i.mapUrl) ? `<a class="btn btn-map" href="${safeUrl(i.mapUrl)}" target="_blank" rel="noreferrer">ナビで案内</a>` : ''}
        </div>

        <div class="actions actions-sub">
          ${safeUrl(i.rakutenAffiliateUrl) ? `<a class="btn btn-rakuten" href="${safeUrl(i.rakutenAffiliateUrl)}" target="_blank" rel="sponsored noreferrer">楽天で関連商品を見る</a>` : ''}
          ${safeUrl(i.amazonAffiliateUrl) ? `<a class="btn btn-amazon" href="${safeUrl(i.amazonAffiliateUrl)}" target="_blank" rel="sponsored noreferrer">Amazonで関連商品を見る</a>` : ''}
        </div>
      </article>
    `).join('');
  }

  [q,pref,cat,season,largeDog].forEach(el => el && el.addEventListener('input', render));
  [q,pref,cat,season,largeDog].forEach(el => el && el.addEventListener('change', render));

  if (quick){
    quick.innerHTML = ['イベント','カフェ','ドッグラン'].map(c => `<button class="chip-btn" data-cat="${c}">${c}</button>`).join('');
    quick.querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => { cat.value = btn.dataset.cat; render(); }));
  }

  render();
}

loadItems().then(renderApp).catch((e) => {
  console.error(e);
  document.getElementById('count').textContent = '読み込み失敗';
});

setInterval(() => {
  loadItems().then(renderApp).catch(() => {});
}, 5 * 60 * 1000);
