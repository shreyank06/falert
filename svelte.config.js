import preprocess from 'svelte-preprocess';
import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    kit: {
        adapter: adapter(),

        // hydrate the <div id="svelte"> element in src/app.html
        files: {
            template: 'falert/frontend/app.html',
            assets: 'falert/frontend/static',
            hooks: 'falert/frontend/hooks',
            lib: 'falert/frontend/lib',
            routes: 'falert/frontend/route',
            serviceWorker: 'falert/frontend/service-worker',
        },

        vite: {
            server: {
                fs: {
                    allow: ['falert/frontend'],
                }
            }
        }
    },

    preprocess: [
        preprocess({
            postcss: true,
        }),
    ],
};

export default config;
