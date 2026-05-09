async function loadItems() {
  const paths = ['./data/events.json', './データ/events.json'];
  let lastErr;
  for (const p of paths) {
    try {
      const res = await fetch(p, { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status} for ${p}`);
      return await res.json();
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error('events.json not found');
}

const esc = (s='') => String(s).replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
const safeUrl = (u='') => /^https:\/\//.test(String(u)) ? String(u) : '';

function renderFeatured(items){
  const featured = document.getElementById('featured');
  if (!featured) return;
  const picks = items.filter(i => ['山・ハイキング','カフェ','キャンプ','ホテル'].includes(i.category)).slice(0,4);
  featured.innerHTML = `
    <h2 class="subhead">迷った時のおすすめカテゴリ</h2>
    <div class="quick-grid">${picks.map(i => `<article class="card compact"><p class="badge">${esc(i.category)}</p><h4>${esc(i.title)}</h4><p class="sub">${esc(i.prefecture)}・${esc(i.area)}</p></article>`).join('')}</div>
  `;
}

function renderApp(items) {
  const updated = document.getElementById('lastUpdated');
  const latest = items.map(i => i.updatedAt).filter(Boolean).sort().pop();
  if (updated && latest) updated.textContent = `最終更新: ${latest.replace('T', ' ').replace('Z', ' UTC')}`;

  const prefs=['すべて',...new Set(items.map(i=>i.prefecture))];
  const cats=['すべて',...new Set(items.map(i=>i.category))];
  const q=document.getElementById('q'); const pref=document.getElementById('pref'); const cat=document.getElementById('cat'); const season=document.getElementById('season'); const largeDog=document.getElementById('largeDog');
  const quick = document.getElementById('quick')
  pref.innerHTML = ''; cat.innerHTML = '';
  prefs.forEach(v=>pref.add(new Option(v,v))); cats.forEach(v=>cat.add(new Option(v,v)));

  function render(){
    const kw=q.value.trim().toLowerCase();
    const filtered=items.filter(i=>(!kw||`${i.title} ${i.summary}`.toLowerCase().includes(kw))&&(pref.value==='すべて'||i.prefecture===pref.value)&&(cat.value==='すべて'||i.category===cat.value)&&((season?.value||'すべて')==='すべて'||(i.seasons||[]).includes(season.value))).sort((a,b)=> {
      const freshness = String(b.updatedAt || '').localeCompare(String(a.updatedAt || ''));
      if (freshness !== 0) return freshness;
      return largeDog?.checked ? (b.largeDogFriendly===true)-(a.largeDogFriendly===true) : 0;
    });
    document.getElementById('count').textContent=`${filtered.length} 件`;
    document.getElementById('list').innerHTML=filtered.map(i=>`<article class="card"><div class="badges"><span class="badge">${esc(i.status||'要確認')}</span><span class="badge">${esc(i.category)}</span></div><h3>${esc(i.title)}</h3><p class="sub">${esc(i.prefecture)}・${esc(i.area)} / ${esc(i.date)}</p><p>${esc(i.summary)}</p><div class="actions">${safeUrl(i.url)?`<a class="btn" href="${safeUrl(i.url)}" target="_blank" rel="noreferrer">公式サイトを見る</a>`:'<span class="sub">公式確認中</span>'}${safeUrl(i.mapUrl)?`<a class="btn btn-map" href="${safeUrl(i.mapUrl)}" target="_blank" rel="noreferrer">ナビで案内</a>`:''}${safeUrl(i.affiliateUrl)?`<a class="btn btn-sub" href="${safeUrl(i.affiliateUrl)}" target="_blank" rel="sponsored noreferrer">関連商品・宿を予約</a>`:''}</div></article>`).join('');
  }
  [q,pref,cat,season,largeDog].forEach(el=>el && el.addEventListener('input',render));
  if (quick) {
    quick.innerHTML = ['山・ハイキング','カフェ','キャンプ','ホテル'].map(c => `<button class="chip-btn" data-cat="${c}">${c}</button>`).join('');
    quick.querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => {cat.value = btn.dataset.cat; render();}));
  }
  [q,pref,cat,season,largeDog].forEach(el=>el && el.addEventListener('change',render));
  render();
  renderFeatured(items);
}

loadItems().then(renderApp).catch((e) => {
  console.error(e);
  document.getElementById('count').textContent = '読み込み失敗';
});

setInterval(() => {
  loadItems().then(renderApp).catch(() => {});
}, 5 * 60 * 1000);
