<template>
    <div></div>
  </template>
  
  <script>
  import * as THREE from 'three';
  
  export default {
    name: 'SeaMonkey',
    props: {
      position: {
        type: Object,
        required: true,
      },
    },
    mounted() {
      this.createSeaMonkey();
    },
    methods: {
      createSeaMonkey() {
        // Sea Monkey Model (Sphere)
        const geometry = new THREE.SphereGeometry(1, 16, 16);
        const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
        this.seaMonkey = new THREE.Mesh(geometry, material);
        this.seaMonkey.position.set(
          this.position.x,
          this.position.y,
          this.position.z
        );
        this.$parent.scene.add(this.seaMonkey);
      },
    },
  };
  </script>