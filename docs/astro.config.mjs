import starlight from "@astrojs/starlight";
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://openspective.aryantah.com",
  integrations: [
    starlight({
      title: "openspective",
      description: "Open-source, self-hosted drop-in replacement for Google's Perspective API.",
      logo: { src: "./src/assets/logo.svg" },
      favicon: "/favicon.svg",
      social: [{ icon: "github", label: "GitHub", href: "https://github.com/aryan-tah/openspective" }],
      editLink: { baseUrl: "https://github.com/aryan-tah/openspective/edit/main/docs/" },
      lastUpdated: true,
      customCss: ["./src/styles/theme.css"],
      components: { PageTitle: "./src/components/PageTitle.astro" },
      sidebar: [
        { label: "Start here", items: ["getting-started", "guides/configuration", "guides/deploy"] },
        {
          label: "Migrate from Perspective",
          items: [
            "migrate/overview",
            "migrate/coral",
            "migrate/discourse",
            "migrate/python",
            "migrate/research",
            "migrate/other-clients",
          ],
        },
        {
          label: "Reference",
          items: ["reference/api", "reference/attributes", "reference/compatibility", "reference/errors"],
        },
      ],
      head: [
        { tag: "link", attrs: { rel: "preconnect", href: "https://fonts.googleapis.com" } },
        { tag: "link", attrs: { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: true } },
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "https://fonts.googleapis.com/css2?family=Geist:wght@400..700&family=Geist+Mono:wght@400..600&display=swap",
          },
        },
      ],
    }),
  ],
});
