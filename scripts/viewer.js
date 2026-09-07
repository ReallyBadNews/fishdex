import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { installInteractionGuards } from "./viewer-interaction.js";
try {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(innerWidth, innerHeight);
  renderer.setClearColor(0xe6e9dc, 0);
  document.body.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    36,
    innerWidth / innerHeight,
    0.01,
    50,
  );
  camera.position.set(0, 0.28, 4.5);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x566348, 2.5));
  const key = new THREE.DirectionalLight(0xfff1d1, 3.0);
  key.position.set(-2, 3, 4);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0xc4e6f5, 2.0);
  rim.position.set(2, 1, -3);
  scene.add(rim);
  const controls = new OrbitControls(camera, renderer.domElement);
  installInteractionGuards(renderer.domElement, (message) => {
    window.ReactNativeWebView?.postMessage(message);
  });
  controls.enablePan = false;
  controls.minDistance = 1.5;
  controls.maxDistance = 7;
  const render = () => renderer.render(scene, camera);
  controls.addEventListener("change", render);
  new GLTFLoader().parse(
    Uint8Array.from(atob(window.MODEL), (c) => c.charCodeAt(0)).buffer,
    "",
    (gltf) => {
      const model = gltf.scene;
      const box = new THREE.Box3().setFromObject(model);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      model.position.sub(center);
      const group = new THREE.Group();
      group.add(model);
      group.scale.setScalar(2.6 / Math.max(size.x, size.y, size.z));
      scene.add(group);
      render();
      document.getElementById("loading").remove();
      window.ReactNativeWebView?.postMessage("ready");
    },
    () => {
      document.getElementById("loading").textContent =
        "Could not open this model. Close and try again.";
    },
  );
  addEventListener("resize", () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
    render();
  });
  document.getElementById("reset").onclick = () => {
    controls.reset();
    render();
  };
} catch (e) {
  document.getElementById("loading").textContent =
    "3D could not start on this device.";
  window.ReactNativeWebView?.postMessage("error");
}
