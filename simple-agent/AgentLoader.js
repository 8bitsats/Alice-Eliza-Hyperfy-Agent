import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

// Import from node client
import { System } from '../hyperfy/build/world-node-client.js';

// import { VRMLoaderPlugin } from "@pixiv/three-vrm";
// --- Mock Browser Environment for Loaders ---
// These might need adjustment based on GLTFLoader/VRMLoaderPlugin requirements
if (typeof globalThis !== 'undefined') {
    // Mock URL if not globally available or needs specific behavior
    // globalThis.URL = URL; // Usually available in modern Node

    // Mock self if needed by any dependency
    // globalThis.self = globalThis; 

    // Mock window minimally
    globalThis.window = globalThis.window || globalThis; 

    // Mock document minimally for GLTFLoader
    globalThis.document = globalThis.document || {
        createElementNS: (ns, type) => {
            if (type === 'img') {
                // Basic mock for image elements if texture loading is attempted (though we aim to bypass it)
                return { 
                    src: '', 
                    onload: () => {}, 
                    onerror: () => {} 
                };
            }
            // Default mock for other elements like canvas
            return { style: {} };
        },
        createElement: (type) => {
             if (type === 'img') {
                 return { src: '', onload: () => {}, onerror: () => {} };
             }
             // Basic canvas mock if needed
             if (type === 'canvas') {
                 return { getContext: () => null, style: {} };
             }
             return { style: {} }; // Default
        }
        // Add more document mocks if loader errors indicate they are needed
    };

    // Polyfill fetch if using older Node version without native fetch
    // globalThis.fetch = fetch; 
}
// --- End Mocks ---


export class AgentLoader extends System {
    constructor(world) {
        super(world);
        this.promises = new Map();
        this.results = new Map();
        this.gltfLoader = new GLTFLoader();

        // --- Dummy Scene for Hooks ---
        // Create one dummy object to act as the scene target for all avatar loads
        this.dummyScene = new THREE.Object3D();
        this.dummyScene.name = "AgentLoaderDummyScene";
        // -----------------------------

        // --- Attempt to register VRM plugin ---
        // try {
        //     this.gltfLoader.register(parser => new VRMLoaderPlugin(parser, {
        //         autoUpdateHumanBones: false
        //     }));
        //     console.log("[AgentLoader] VRMLoaderPlugin registered.");
        // } catch (vrmError) {
        //     console.error("[AgentLoader] Warning: Failed to register VRMLoaderPlugin. VRM-specific features might be unavailable.", vrmError);
        // }
        // ---------------------------------------
    }

    // --- Dummy Preload Methods ---
    preload(type, url) {
        // No-op for agent
    }
    execPreload() {
        // No-op for agent
        // ClientNetwork calls this after snapshot, so it must exist.
        console.log("[AgentLoader] execPreload called (No-op).");
    }
    // ---------------------------


    // --- Basic Cache Handling ---
    // ... (has, get methods remain the same) ...
    has(type, url) { const key = `${type}/${url}`; return this.results.has(key) || this.promises.has(key); }
    get(type, url) { const key = `${type}/${url}`; return this.results.get(key); }
    // ---------------------------

    resolveUrl(url) {
        // ... (resolveUrl implementation remains the same) ...
        if (typeof url !== 'string') { console.error(`[AgentLoader] Invalid URL type provided: ${typeof url}`); return null; }
        if (url.startsWith('asset://')) {
            if (!this.world.assetsUrl) { console.error("[AgentLoader] Cannot resolve asset:// URL, world.assetsUrl not set."); return null; }
            const filename = url.substring('asset://'.length);
            const baseUrl = this.world.assetsUrl.replace(/[/\\\\]$/, ''); // Remove trailing slash (either / or \)
            return `${baseUrl}/${filename}`;
        }
        if (url.startsWith('http://') || url.startsWith('https://')) { return url; }
        console.warn(`[AgentLoader] Cannot resolve potentially relative URL without base: ${url}`);
        return url;
    }

    async load(type, url) {
        const key = `${type}/${url}`;
        if (this.promises.has(key)) {
            return this.promises.get(key);
        }

        const httpUrl = this.resolveUrl(url);
        if (!httpUrl) {
            const errorMsg = `[AgentLoader] Failed to resolve URL: ${url}`;
            console.error(errorMsg);
            return Promise.reject(new Error(errorMsg));
        }

        console.log(`[AgentLoader] Loading ${type}: ${url} -> ${httpUrl}`);

        const promise = fetch(httpUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`[AgentLoader] HTTP error! status: ${response.status} for ${httpUrl}`);
                }
                return response.arrayBuffer();
            })
            .then(arrayBuffer => {
                 console.log(`[AgentLoader] Fetched ${httpUrl} (${arrayBuffer.byteLength} bytes)`);

                // --- GLTF/GLB/VRM Parsing ---
                if (type === 'model' || type === 'avatar' || type === 'emote') {
                    return new Promise((resolve, reject) => {
                        this.gltfLoader.parse(arrayBuffer, '',
                            (gltf) => {
                                console.log(`[AgentLoader] GLTFLoader parsed ${httpUrl} successfully.`);
                                let resultObject;

                                if (type === 'model') {
                                    // Reuse glbToNodes if adapted for Node
                                    // For now, just return the essential scene graph
                                    resultObject = {
                                        gltf: gltf,
                                        toNodes: () => {
                                           // Basic implementation: return the scene directly
                                           // Might need adaptation based on glbToNodes logic
                                           return gltf.scene ? gltf.scene.clone(true) : new THREE.Group(); 
                                        }
                                    };
                                } else if (type === 'avatar') {
                                    // Simple VRM factory implementation
                                    const factory = gltf.userData.vrm
                                        ? {
                                            type: 'vrm',
                                            gltf: gltf,
                                            setup: (material) => {
                                                console.log("[AgentLoader] setupMaterial called with material:", material);
                                            }
                                          }
                                        : null;

                                    // Simple node creation implementation
                                    const rootNode = new THREE.Group();
                                    rootNode.userData.id = '$root';
                                    
                                    // --- Create Dummy Hooks ---
                                    const dummyHooks = {
                                        scene: this.dummyScene, // Provide the dummy scene object
                                        // Add other minimal properties if activate complains about them being undefined
                                        camera: null, 
                                        octree: null,
                                        loader: this, // Can pass self if needed by avatar node
                                        setupMaterial: (material) => {
                                            console.log("[AgentLoader] setupMaterial called with material:", material);
                                        },
                                        camera: new THREE.Object3D(),
                                    };
                                    // --------------------------
                                    
                                    // Create a simple avatar node for our purposes
                                    const avatarNode = new THREE.Group();
                                    avatarNode.userData.id = 'avatar';
                                    avatarNode.userData.nodeType = 'avatar';
                                    avatarNode.userData.factory = factory;
                                    avatarNode.userData.hooks = dummyHooks;
                                    rootNode.add(avatarNode);

                                    resultObject = {
                                        gltf: gltf,
                                        factory,
                                        hooks: dummyHooks, // Store dummy hooks
                                        toNodes: (customHooks = null) => {
                                             // Clone and potentially override hooks if needed, 
                                             // but agent likely doesn't use customHooks
                                             const clonedRoot = rootNode.clone(true);
                                             // If customHooks were provided and needed, apply them here.
                                             // For the agent, we likely just return the clone with dummy hooks.
                                             return clonedRoot;
                                        },
                                    };
                                } else if (type === 'emote') {
                                     // Reuse emote factory if adapted for Node
                                     // For now, return minimal structure
                                     resultObject = {
                                         gltf: gltf,
                                         toClip: (opts) => {
                                             // Basic implementation: find first animation clip
                                             return gltf.animations && gltf.animations.length > 0 
                                                    ? gltf.animations[0] 
                                                    : null;
                                         }
                                     };
                                } else {
                                    reject(new Error(`Internal error: Unhandled GLTF type: ${type}`));
                                    return;
                                }

                                this.results.set(key, resultObject);
                                resolve(resultObject);

                            },
                            (error) => {
                                console.error(`[AgentLoader] GLTFLoader parse error for ${httpUrl}:`, error);
                                reject(error);
                            }
                        );
                    });
                }
                // ... (rest of the handlers for script, json, etc.) ...
                else if (type === 'script') { /* ... */ }
                 else if (type === 'json') { /* ... */ }
                else { /* ... */ }
            })
            .then(result => {
                console.log(`[AgentLoader] Successfully loaded and processed ${key}`);
                return result;
            })
            .catch(error => {
                 console.error(`[AgentLoader] Failed loading ${type} from ${httpUrl}:`, error);
                 this.promises.delete(key);
                 throw error;
            });

        this.promises.set(key, promise);
        return promise;
    }
}
