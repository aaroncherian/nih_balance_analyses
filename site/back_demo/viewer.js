// viewer.js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/**
 * Reusable 3D marker viewer with slider + play/pause + fps.
 * Expected data schema: { positions: [F][M][3] }
 */
export class MarkerViewer {
  constructor(opts) {
    this.opts = Object.assign({
      sceneEl: '#scene',
      hudEl: '#hud',
      dataUrl: 'data.json',
      scale: 1.0,
      fps: 30,
      loop: true,
      pointColor: 0x2f6efc,
      pointRadiusWorld: 20,   // this * scale → actual radius
      onFrameChange: null,    // (k) => void
    }, opts || {});

    this.container = this._elt(this.opts.sceneEl);
    this.hud = this._elt(this.opts.hudEl);

    // state
    this.positions = null;    // [F][M][3]
    this.F = 0; this.M = 0;
    this.k = 0;
    this.playing = false;
    this.lastT = 0;

    // three
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.controls = null;
    this.spheres = [];

    // ui
    this.slider = null;
    this.label = null;
    this.playBtn = null;
    this.fpsInput = null;

    // init
    this._initThree();
    this._initUI();
    this._loadData(this.opts.dataUrl);
    this._animate = this._animate.bind(this);
    requestAnimationFrame(this._animate);
  }

  // ----------------- setup -----------------
  _elt(sel) {
    const el = (typeof sel === 'string') ? document.querySelector(sel) : sel;
    if (!el) throw new Error(`Element not found: ${sel}`);
    return el;
  }

  _initThree() {
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.container.appendChild(this.renderer.domElement);

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xffffff);

    this.camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100000);
    this.camera.up.set(0,0,1);
    this.camera.position.set(1000, -1000, 1000);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;

    // light + grid
    this.scene.add(new THREE.AmbientLight(0xffffff, 1));
    const grid = new THREE.GridHelper(4, 8);
    grid.rotation.x = Math.PI/2;
    grid.material.opacity = 0.25;
    grid.material.transparent = true;
    this.scene.add(grid);

    // resize
    const resize = () => {
      const w = this.container.clientWidth || window.innerWidth;
      const h = this.container.clientHeight || (window.innerHeight - 80);
      this.renderer.setSize(w, h);
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
    };
    new ResizeObserver(resize).observe(this.container);
    resize();

    // keyboard: space toggles play/pause
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space') { e.preventDefault(); this.toggle(); }
    });
  }

  _initUI() {
    this.hud.style.display = 'flex';
    this.hud.style.gap = '8px';
    this.hud.style.alignItems = 'center';

    // slider + label
    const slider = document.createElement('input');
    slider.type = 'range';
    slider.min = '0';
    slider.max = '0';
    slider.value = '0';
    slider.step = '1';
    slider.style.width = '300px';

    const label = document.createElement('span');
    label.textContent = '0';

    // play button
    const playBtn = document.createElement('button');
    playBtn.textContent = 'Play';

    // fps input
    const fpsWrap = document.createElement('label');
    fpsWrap.style.display = 'flex';
    fpsWrap.style.alignItems = 'center';
    fpsWrap.style.gap = '4px';
    fpsWrap.textContent = 'FPS ';
    const fpsInput = document.createElement('input');
    fpsInput.type = 'number';
    fpsInput.value = String(this.opts.fps);
    fpsInput.min = '1'; fpsInput.max = '120'; fpsInput.step = '1';
    fpsInput.style.width = '60px';
    fpsWrap.appendChild(fpsInput);

    // loop checkbox
    const loopWrap = document.createElement('label');
    loopWrap.style.display = 'flex';
    loopWrap.style.alignItems = 'center';
    loopWrap.style.gap = '4px';
    loopWrap.textContent = 'Loop ';
    const loopCb = document.createElement('input');
    loopCb.type = 'checkbox';
    loopCb.checked = !!this.opts.loop;
    loopWrap.appendChild(loopCb);

    // append
    this.hud.append(slider, label, playBtn, fpsWrap, loopWrap);

    // wire
    slider.addEventListener('input', e => {
      const k = Number(e.target.value);
      this.setFrame(k);
    });
    playBtn.addEventListener('click', () => this.toggle());
    fpsInput.addEventListener('change', () => {
      // clamp in tick()
    });
    loopCb.addEventListener('change', () => {
      this.opts.loop = loopCb.checked;
    });

    // keep refs
    this.slider = slider;
    this.label = label;
    this.playBtn = playBtn;
    this.fpsInput = fpsInput;
  }

  async _loadData(url) {
    const res = await fetch(url);
    const data = await res.json();
    const positions = data.positions;
    this.positions = positions;
    this.F = positions.length;
    this.M = positions[0].length;


        // let external code (plots) initialize on the raw data
    if (typeof this.opts.onDataLoaded === 'function') {
    this.opts.onDataLoaded(data);
    }
    // prep slider
    this.slider.max = String(this.F - 1);

    // build spheres once
    const S = this.opts.scale;
    const geom = new THREE.SphereGeometry(this.opts.pointRadiusWorld * S);
    const mat  = new THREE.MeshStandardMaterial({ color: this.opts.pointColor });
    for (let i = 0; i < this.M; i++) {
      const s = new THREE.Mesh(geom, mat);
      this.scene.add(s);
      this.spheres.push(s);
    }

    // start at frame 0
    this.setFrame(0);
    // nice default camera view (optional)
    this.camera.position.set(0, -2000 * S, 1500 * S);
    this.controls.target.set(0, 0, 0);
    this.controls.update();
  }

  // ----------------- runtime -----------------
  setFrame(k) {
    if (!this.positions) return;
    this.k = Math.max(0, Math.min(this.F - 1, k));
    const pts = this.positions[this.k];
    const S = this.opts.scale;
    for (let i = 0; i < this.M; i++) {
      const [x, y, z] = pts[i];
      this.spheres[i].position.set(x * S, y * S, z * S);
    }
    this.slider.value = String(this.k);
    this.label.textContent = String(this.k);
    if (typeof this.opts.onFrameChange === 'function') {
      this.opts.onFrameChange(this.k);
    }
  }

  play() {
    if (!this.playing) {
      this.playing = true;
      this.lastT = 0;
    }
  }
  pause() { this.playing = false; }
  toggle() {
    this.playing = !this.playing;
    this.playBtn.textContent = this.playing ? 'Pause' : 'Play';
    this.lastT = 0;
    // animation loop is already running in _animate()
  }

  _animate(t) {
    // playback
    if (this.playing && this.positions) {
      const fps = Math.max(1, Math.min(120, Number(this.fpsInput.value) || this.opts.fps));
      const frameTime = 1000 / fps;
      if (!this.lastT) this.lastT = t;
      if (t - this.lastT >= frameTime) {
        this.lastT += frameTime;
        let k = this.k + 1;
        if (k >= this.F) {
          if (this.opts.loop) k = 0;
          else { this.pause(); this.playBtn.textContent = 'Play'; }
        }
        this.setFrame(k);
      }
    }

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(this._animate);
  }

  // ----------------- cleanup -----------------
  dispose() {
    this.pause();
    window.removeEventListener('keydown', this._keyHandler);
    this.spheres.forEach(s => {
      this.scene.remove(s);
      s.geometry.dispose();
      s.material.dispose();
    });
    this.renderer.dispose();
    this.container.innerHTML = '';
    this.hud.innerHTML = '';
  }
}
