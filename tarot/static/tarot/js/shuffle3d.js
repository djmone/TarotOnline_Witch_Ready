// tarot/static/tarot/js/shuffle3d.js
// Топ-даун, карты создаются динамически, hover-поднятие, анти-мыло, автоподгонка.

(() => {
  const mount = document.getElementById('three-root');
  if (!mount) { console.error('[tarot] #three-root not found'); return; }
  if (typeof THREE === 'undefined') { console.error('[tarot] THREE.js not loaded'); return; }

  // чтение атрибутов
  const dealUrl = mount.dataset.dealUrl;
  const count   = parseInt(mount.dataset.count || '10', 10);

  // сцена
  const scene = new THREE.Scene();

  // ОРТО камера (вид сверху)
  const w = mount.clientWidth, h = mount.clientHeight;
  const frustumSize = 160;
  let aspect = w / h;
  const camera = new THREE.OrthographicCamera(
    -frustumSize * aspect / 2,  frustumSize * aspect / 2,
     frustumSize / 2,           -frustumSize / 2,
     0.1, 1000
  );
  camera.position.set(0, 200, 0);
  camera.up.set(0, 0, -1);
  camera.lookAt(0, 0, 0);

  // рендер
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  renderer.setSize(w, h);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  mount.appendChild(renderer.domElement);

  // свет
  scene.add(new THREE.AmbientLight(0xffffff, 0.95));

  // размеры карты
  const CARD_W = 34, CARD_H = 54;
  const geom = new THREE.PlaneGeometry(CARD_W, CARD_H);
  geom.rotateX(-Math.PI / 2); // на стол (плоскость XZ)

  // рубашка (локальный файл есть в проекте)
  function tuneTexture(t) {
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = renderer.capabilities.getMaxAnisotropy?.() || 8;
    t.generateMipmaps = true;
    t.minFilter = THREE.LinearMipmapLinearFilter;
    t.magFilter = THREE.LinearFilter;
    t.needsUpdate = true;
    return t;
  }
  const backUrl = mount.dataset.backUrl || '/static/tarot/img/back.jpg';
  const backTex = new THREE.TextureLoader().load(backUrl, tuneTexture);
  const backMat = new THREE.MeshBasicMaterial({
    map: backTex,
    side: THREE.DoubleSide,   // ← добавили
  });

  // текущие карты на столе
  let cards = [];

  // tween позиций
  function tweenXZ(mesh, from, to, ms, done) {
    const t0 = performance.now();
    (function step(now) {
      const p = Math.min(1, (now - t0) / ms);
      mesh.position.x = from.x + (to.x - from.x) * p;
      mesh.position.z = from.z + (to.z - from.z) * p;
      mesh.rotation.y = from.ry + (to.ry - from.ry) * p;
      if (p < 1) requestAnimationFrame(step); else done && done();
    })(t0);
  }

  // hover
  const HOVER_Y = 2.2;
  function attachHover(m) { m.userData.baseY = 0; m.userData.hovered = false; }

  const ray = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  renderer.domElement.addEventListener('mousemove', (ev) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
    ray.setFromCamera(mouse, camera);
    const hits = ray.intersectObjects(cards, false);
    const hovered = new Set(hits.map(h => h.object));
    for (const m of cards) {
      const need = hovered.has(m);
      if (need && !m.userData.hovered) { m.userData.hovered = true;  m.position.y = HOVER_Y; }
      if (!need && m.userData.hovered) { m.userData.hovered = false; m.position.y = 0; }
    }
  });

  // очистка стола
  function clearTable() { for (const m of cards) scene.remove(m); cards = []; }

  // «стопка» для вида (по кнопке Перемешать)
  function shuffle() {
    clearTable();
    const N = Math.max(count, 8);
    for (let i = 0; i < N; i++) {
      const m = new THREE.Mesh(geom, backMat);
      m.position.set(-60 + Math.random()*2-1, 0, 46 + Math.random()*2-1);
      m.rotation.y = (Math.random()-0.5)*0.1;
      attachHover(m);
      scene.add(m);
      cards.push(m);
    }
  }

  // подгонка координат под окно
  function fitTransform(points) {
    if (!points.length) return { cx:0, cz:0, scale:1 };
    let minX=Infinity, maxX=-Infinity, minZ=Infinity, maxZ=-Infinity;
    for (const p of points) { minX=Math.min(minX,p.x); maxX=Math.max(maxX,p.x); minZ=Math.min(minZ,p.z); maxZ=Math.max(maxZ,p.z); }
    const cx = (minX+maxX)/2, cz = (minZ+maxZ)/2;
    const viewW = camera.right - camera.left, viewH = camera.top - camera.bottom;
    const needW = (maxX-minX) + CARD_W + 20, needH = (maxZ-minZ) + CARD_H + 20;
    const scale = Math.min(viewW/needW, viewH/needH, 1.0);
    return { cx, cz, scale };
  }

  function getCsrf() {
    const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  async function deal() {
    if (!dealUrl) { console.error('[tarot] no dealUrl'); return; }
    const resp = await fetch(dealUrl, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf(), 'Accept':'application/json' },
      credentials: 'same-origin'
    });
    if (!resp.ok) {
      console.error('[tarot] deal failed', resp.status, await resp.text());
      return;
    }
    const data = await resp.json(); // [{x,z,img_url,reversed}, ...]

    clearTable();
    const fit = fitTransform(data.map(d => ({x:d.x, z:d.z})));

    for (const info of data) {
      // создаём карту рубашкой
      const m = new THREE.Mesh(geom, backMat);
      m.position.set(-60, 0, 46);
      attachHover(m);
      scene.add(m);
      cards.push(m);

      // целевая позиция (вписываем в окно)
      const target = {
        x: (info.x - fit.cx) * fit.scale,
        z: (info.z - fit.cz) * fit.scale + 4,
        ry: 0
      };

      // прилёт
      await new Promise(done => tweenXZ(m, {x:m.position.x,z:m.position.z,ry:m.rotation.y}, target, 420, done));

      // загрузка лицевой
      const faceMat = await new Promise(res => {
        new THREE.TextureLoader().load(
          info.img_url || '/static/tarot/img/placeholder.jpg',
          t => {
            tuneTexture(t);
            res(new THREE.MeshBasicMaterial({
              map: t,
              side: THREE.DoubleSide,   // ← вот это добавили
            }));
          },
          undefined,
          () => res(backMat)
        );
      });

      // flip по Y (вид сверху)
      // flip по Y (переворот с рубашки на лицо)
      await new Promise(done => {
        const t0 = performance.now(), dur = 360;
        (function step(now) {
          const p = Math.min(1,(now-t0)/dur);
          m.rotation.y = Math.PI * p;
          if (p >= 0.5 && m.material !== faceMat) m.material = faceMat;
          if (p < 1) requestAnimationFrame(step); else done();
        })(t0);
      });

      // правильная «перевёрнутость» Таро — вокруг Z
      m.rotation.z = info.reversed ? Math.PI : 0;   // ← вот это ключ

    }
  }

  // resize
  window.addEventListener('resize', () => {
    const w = mount.clientWidth, h = mount.clientHeight;
    renderer.setSize(w, h);
    aspect = w/h;
    camera.left   = -frustumSize * aspect / 2;
    camera.right  =  frustumSize * aspect / 2;
    camera.top    =  frustumSize / 2;
    camera.bottom = -frustumSize / 2;
    camera.updateProjectionMatrix();
  });

  // цикл
  (function loop(){ requestAnimationFrame(loop); renderer.render(scene,camera); })();

  // кнопки
  document.getElementById('btn-shuffle')?.addEventListener('click', shuffle);
  document.getElementById('btn-deal')?.addEventListener('click', deal);

  // старт — просто «кучка» для вида
  shuffle();
})();
