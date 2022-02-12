import _ from 'https://cdn.skypack.dev/lodash';

import hotwiredTurbo from 'https://cdn.skypack.dev/@hotwired/turbo';
import {Controller, Application} from 'https://cdn.skypack.dev/@hotwired/stimulus';
import { useIntersection } from 'https://cdn.skypack.dev/stimulus-use'

class CourseFilter extends Controller {
    static targets = [ "query", "tag", "filterable" ]

    filter(event) {
      let lowerCaseFilterTerm = this.queryTarget.value.toLowerCase()
      let selectedTags = this.tagTargets
        .filter((el) => el.checked)
        .map((el) => el.getAttribute("data-tag-name"));

      this.filterableTargets.forEach((el, i) => {
        let key =  el.getAttribute("data-filter-key");
        let tags = el.getAttribute("data-tags").split(" ");
        let containsText = key.toLowerCase().includes( lowerCaseFilterTerm );
        let containsTags = _.difference(selectedTags, tags).length === 0;
        el.classList.toggle("filter--filtered", !containsText || !containsTags)
    })
  }
}

class Search extends Controller {
    static targets = ["input", "output", "submit"]

    initialize() {
      this.search = _.debounce(this.search, 200, {trailing: true})
    }

    search(event) {
      this.outputTarget.value = this.inputTarget.value
      this.submitTarget.click();
    }
}

import bundledEsModulesPdfjsDist from 'https://cdn.skypack.dev/@bundled-es-modules/pdfjs-dist@2.5.207-rc1';
let pdfjs = bundledEsModulesPdfjsDist
pdfjs.GlobalWorkerOptions.workerSrc = "https://cdn.jsdelivr.net/npm/pdfjs-dist@2.5.207/build/pdf.worker.js"


class Viewer extends Controller {
    static targets = ["renderer"]
    static values = {src: String, hasPage: Boolean}

    static options = {
        threshold: 0, // default
    }

    async connect() {
        //useIntersection(this, this.options)

        let options = {
            root: this.element,
            rootMargin: '0px',
            threshold: 0
        }
        let callback = (e) => {
            console.log("OBS", e)
        }

        this.observer = new IntersectionObserver(callback, options);

        let loadingTask = pdfjs.getDocument(this.srcValue);

        loadingTask.onProgress = (data) => {
            //this.loaderTarget.setAttribute("value", 100 * data.loaded / data.total);
        }

        this.pdf = await loadingTask.promise;
        this.pages = {};

        for (let i = 1; i <= this.pdf.numPages; i++) {
            this.pages[i] = await this.pdf.getPage(i);

            let wrapper = document.createElement("div");
            wrapper.classList.add("page-wrapper");
            wrapper.style['aspectRatio'] = this.getPageRatio(i);
            wrapper.setAttribute("data-action", "appear@window->viewer#appear")
            wrapper.setAttribute("data-viewer-page-param", i)
            //this.observer.observe(wrapper)

            this.rendererTarget.appendChild(wrapper);

            // let canvas = document.createElement("canvas")
            // this.rendererTarget.appendChild(canvas);
            // await this.loadPage(i, canvas);
            // if(i === 1) {
            //   this.hasPageValue = true
            // }
            // if(i > 10) {
            //     // load slower after 10 pages to relieve the CPU
            //     await new Promise(resolve => setTimeout(resolve, 50))
            // }

        }

    }

    appear(entry) {
        console.log("Appear", entry);
    }

    disappear(entry) {
        // ...
    }

    getPageRatio(i) {
        let page = this.pages[i];
        let viewport = page.getViewport({scale: 1,});
        return `${viewport.width} / ${viewport.height}`;
    }

    async loadPage(i) {
        let page = await this.pdf.getPage(i);
        let viewport = page.getViewport({scale: 1,});

        // retina support
        let screenRatio = window.devicePixelRatio || 1

        let scale = screenRatio * Math.max(window.innerWidth / viewport.width, window.innerHeight / viewport.height)

        canvas.width = Math.floor(viewport.width * scale);
        canvas.height = Math.floor(viewport.height * scale);
        canvas.style.width = "90vw";

        let transform = scale !== 1
            ? [scale, 0, 0, scale, 0, 0]
            : null;

        // Render PDF page into canvas context.
        let renderContext = {
            canvasContext: canvas.getContext('2d'),
            transform,
            viewport,
        };
        await page.render(renderContext);

        if(i < 2) {
            // The page might be loading while being visible in the viewport
            // se we want to make sure that the browser has rendered the canvas
            // before starting the reveal animation
            await new Promise((resolve) => setTimeout(resolve, 10));
        }

        canvas.setAttribute("data-viewer-ready", "")
    }

}

const application = Application.start()

application.register("course-filter", CourseFilter);
application.register("search", Search);
application.register("viewer", Viewer);
application.debug = true;
