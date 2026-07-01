import { defineConfig } from "vitepress";

export const SITE_URL = "https://muhammad-fiaz.github.io/logly";
export const SITE_NAME = "Logly";
export const SITE_DESCRIPTION =
  "A Rust-powered, high-performance logging library for Python with structured sinks, custom levels, rotation, compression, and telemetry integrations.";

// Google Analytics and Google Tag Manager IDs
export const GA_ID = "G-6BVYCRK57P";
export const GTM_ID = "GTM-P4M9T8ZR";

// Google AdSense Client ID
export const ADSENSE_CLIENT_ID = "ca-pub-2040560600290490";

export const KEYWORDS =
  "logly, python, logging, rust, performance, structured-logging, fastapi, django, flask, high-performance, developer-tools, pyo3";

export default defineConfig({
  lang: "en-US",
  title: SITE_NAME,
  description: SITE_DESCRIPTION,
  base: "/logly/",
  lastUpdated: true,
  cleanUrls: true,

  sitemap: {
    hostname: SITE_URL,
  },

  head: [
    [
      "meta",
      { name: "viewport", content: "width=device-width, initial-scale=1.0" },
    ],
    ["meta", { name: "google-adsense-account", content: ADSENSE_CLIENT_ID }],
    ["meta", { name: "title", content: SITE_NAME }],
    ["meta", { name: "description", content: SITE_DESCRIPTION }],
    ["meta", { name: "keywords", content: KEYWORDS }],
    ["meta", { name: "author", content: "Muhammad Fiaz" }],
    ["meta", { name: "robots", content: "index, follow" }],
    ["meta", { name: "language", content: "English" }],
    ["meta", { name: "revisit-after", content: "7 days" }],
    ["meta", { name: "generator", content: "VitePress" }],

    // Open Graph
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:url", content: SITE_URL }],
    ["meta", { property: "og:title", content: SITE_NAME }],
    ["meta", { property: "og:description", content: SITE_DESCRIPTION }],
    ["meta", { property: "og:image", content: `${SITE_URL}/cover.png` }],
    ["meta", { property: "og:image:width", content: "1200" }],
    ["meta", { property: "og:image:height", content: "630" }],
    [
      "meta",
      {
        property: "og:image:alt",
        content: "Logly - Rust-Powered Logging for Python",
      },
    ],
    ["meta", { property: "og:site_name", content: SITE_NAME }],
    ["meta", { property: "og:locale", content: "en_US" }],

    // Twitter
    ["meta", { name: "twitter:card", content: "summary_large_image" }],
    ["meta", { name: "twitter:url", content: SITE_URL }],
    ["meta", { name: "twitter:title", content: SITE_NAME }],
    ["meta", { name: "twitter:description", content: SITE_DESCRIPTION }],
    ["meta", { name: "twitter:image", content: `${SITE_URL}/cover.png` }],
    ["meta", { name: "twitter:creator", content: "@muhammadfiaz_" }],

    // Canonical
    ["link", { rel: "canonical", href: SITE_URL }],

    // Favicons
    ["link", { rel: "icon", href: "/logly/favicon.ico", sizes: "48x48" }],
    [
      "link",
      {
        rel: "icon",
        href: "/logly/favicon-32x32.png",
        type: "image/png",
        sizes: "32x32",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        href: "/logly/favicon-16x16.png",
        type: "image/png",
        sizes: "16x16",
      },
    ],
    [
      "link",
      {
        rel: "apple-touch-icon",
        href: "/logly/apple-touch-icon.png",
        sizes: "180x180",
      },
    ],
    ["link", { rel: "manifest", href: "/logly/site.webmanifest" }],

    // Theme color
    ["meta", { name: "theme-color", content: "#4f46e5" }],

    // Google Analytics
    [
      "script",
      {
        async: "",
        src: `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`,
      },
    ],
    [
      "script",
      {},
      `window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', '${GA_ID}');`,
    ],

    // Google Tag Manager
    ...(GTM_ID
      ? ([
          [
            "script",
            {},
            `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start': new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0], j=d.createElement(s), dl=l!='dataLayer'?'&l='+l:''; j.async=true; j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl; f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','${GTM_ID}');`,
          ],
          [
            "noscript",
            {},
            `<iframe src="https://www.googletagmanager.com/ns.html?id=${GTM_ID}" height="0" width="0" style="display:none;visibility:hidden"></iframe>`,
          ],
        ] as [string, Record<string, string>, string][])
      : []),

    // Google AdSense
    [
      "script",
      {
        async: "",
        src: `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT_ID}`,
        crossorigin: "anonymous",
      },
    ],
  ],

  ignoreDeadLinks: [/.*\.zig$/, /.*\.py$/],

  transformPageData(pageData) {
    const pageTitle = pageData.title || SITE_NAME;
    const pageDescription = pageData.description || SITE_DESCRIPTION;
    const canonicalUrl = `${SITE_URL}/${pageData.relativePath.replace(/((^|\/)index)?\.md$/, "$2").replace(/\.md$/, "")}`;

    pageData.frontmatter.head ??= [];
    pageData.frontmatter.head.push(
      ["link", { rel: "canonical", href: canonicalUrl }],
      [
        "meta",
        { property: "og:title", content: `${pageTitle} | ${SITE_NAME}` },
      ],
      ["meta", { property: "og:url", content: canonicalUrl }],
    );

    if (pageData.frontmatter.description) {
      pageData.frontmatter.head.push(
        [
          "meta",
          {
            property: "og:description",
            content: pageData.frontmatter.description,
          },
        ],
        [
          "meta",
          { name: "description", content: pageData.frontmatter.description },
        ],
      );
    }

    const isHome = pageData.relativePath === "index.md";
    const lastUpdated = pageData.lastUpdated
      ? new Date(pageData.lastUpdated).toISOString()
      : new Date().toISOString();

    const graph: Record<string, unknown>[] = [];

    if (isHome) {
      graph.push({
        "@type": "WebSite",
        name: SITE_NAME,
        url: SITE_URL,
        description: SITE_DESCRIPTION,
        author: {
          "@type": "Person",
          name: "Muhammad Fiaz",
          url: "https://github.com/muhammad-fiaz",
        },
      });
    }

    const authorSchema = {
      "@type": "Person",
      name: "Muhammad Fiaz",
      url: "https://muhammadfiaz.com",
      sameAs: [
        "https://github.com/muhammad-fiaz",
        "https://www.linkedin.com/in/muhammad-fiaz-",
        "https://x.com/muhammadfiaz_",
      ],
    };

    const primarySchema: Record<string, unknown> = {
      "@type": isHome ? "SoftwareApplication" : "TechArticle",
      name: isHome ? SITE_NAME : pageTitle,
      description: pageDescription,
      url: canonicalUrl,
      image: `${SITE_URL}/cover.png`,
      author: authorSchema,
      publisher: {
        "@type": "Organization",
        name: SITE_NAME,
        url: SITE_URL,
        logo: { "@type": "ImageObject", url: `${SITE_URL}/favicon.ico` },
      },
    };

    if (isHome) {
      Object.assign(primarySchema, {
        applicationCategory: "DeveloperApplication",
        operatingSystem: "Cross-platform",
        programmingLanguage: "Python",
        offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
        downloadUrl: "https://github.com/muhammad-fiaz/logly",
        license: "https://opensource.org/licenses/MIT",
      });
    } else {
      const pathParts = String(pageData.relativePath).split("/");
      const section =
        pathParts.length > 1
          ? pathParts[0].charAt(0).toUpperCase() + pathParts[0].slice(1)
          : "Documentation";

      Object.assign(primarySchema, {
        headline: pageTitle,
        articleSection: section,
        mainEntityOfPage: { "@type": "WebPage", "@id": canonicalUrl },
        datePublished: "2025-01-01T00:00:00Z",
        dateModified: lastUpdated,
      });
    }
    graph.push(primarySchema);

    const breadcrumbs: Record<string, unknown>[] = [
      { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
    ];

    if (!isHome) {
      const pathParts = String(pageData.relativePath)
        .replace(/\.md$/, "")
        .split("/");
      let currentPath = SITE_URL;

      pathParts.forEach((part, index) => {
        currentPath += `/${part}`;
        const name = part
          .split("-")
          .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
          .join(" ");
        breadcrumbs.push({
          "@type": "ListItem",
          position: index + 2,
          name: name,
          item: index === pathParts.length - 1 ? canonicalUrl : currentPath,
        });
      });
    }

    graph.push({ "@type": "BreadcrumbList", itemListElement: breadcrumbs });

    pageData.frontmatter.head.push([
      "script",
      { type: "application/ld+json" },
      JSON.stringify({ "@context": "https://schema.org", "@graph": graph }),
    ]);
  },

  themeConfig: {
    logo: "/logo.png",
    siteTitle: "Logly",

    nav: [
      { text: "Home", link: "/" },
      { text: "Getting Started", link: "/getting-started" },
      { text: "Guides", link: "/guides/sinks" },
      { text: "Integrations", link: "/integrations/" },
      { text: "API", link: "/api-reference/logger" },
      { text: "Examples", link: "/examples/basic-logging" },
      { text: "Comparison", link: "/comparison" },
      { text: "Sponsor", link: "https://github.com/sponsors/muhammad-fiaz" },
      { text: "GitHub", link: "https://github.com/muhammad-fiaz/logly" },
    ],

    sidebar: {
      "/guides/": [
        {
          text: "Getting Started",
          items: [
            { text: "Introduction", link: "/" },
            { text: "Getting Started", link: "/getting-started" },
          ],
        },
        {
          text: "Core Concepts",
          items: [
            { text: "Sinks", link: "/guides/sinks" },
            {
              text: "Console & Output Control",
              link: "/guides/console-output",
            },
            {
              text: "Source Location & Timestamps",
              link: "/guides/source-location-timestamps",
            },
            { text: "Formatting", link: "/guides/formatting" },
            { text: "Filtering", link: "/guides/filtering" },
            { text: "Context Binding", link: "/guides/context-binding" },
            { text: "Independent Loggers", link: "/guides/independent-loggers" },
            { text: "Custom Levels", link: "/guides/custom-levels" },
            { text: "Concurrency", link: "/guides/concurrency" },
          ],
        },
        {
          text: "File Management",
          items: [
            {
              text: "Rotation, Retention & Compression",
              link: "/guides/rotation-retention-compression",
            },
            { text: "File Logging", link: "/guides/file-logging" },
            {
              text: "Compression Options",
              link: "/guides/compression-options",
            },
            {
              text: "File Directories & Root Dir",
              link: "/guides/file-directories",
            },
          ],
        },
        {
          text: "Error Handling",
          items: [
            { text: "Exception Handling", link: "/guides/exception-handling" },
            {
              text: "Exception Callbacks",
              link: "/guides/exception-callbacks",
            },
          ],
        },
        {
          text: "Integrations",
          items: [
            { text: "FastAPI", link: "/guides/fastapi" },
            { text: "Django", link: "/guides/django" },
            { text: "Flask", link: "/guides/flask" },
            { text: "Stdlib Logging", link: "/guides/stdlib-logging" },
            { text: "Structlog", link: "/guides/structlog" },
            { text: "Rich Console", link: "/guides/rich-console" },
            { text: "Celery", link: "/guides/celery" },
            { text: "Uvicorn", link: "/guides/uvicorn" },
            { text: "Gunicorn", link: "/guides/gunicorn" },
            { text: "Propagate", link: "/guides/propagate" },
          ],
        },
        {
          text: "Advanced",
          items: [
            { text: "Async Sinks", link: "/guides/async-sinks" },
            { text: "Network Logging", link: "/guides/network-logging" },
            { text: "Telemetry", link: "/guides/telemetry" },
            { text: "Parse", link: "/guides/parse" },
            { text: "Configure", link: "/guides/configure" },
            { text: "Color Markup", link: "/guides/color-markup" },
            { text: "Custom Colors", link: "/guides/custom-colors" },
            {
              text: "Color Operations",
              link: "/guides/color-operations",
            },
            { text: "Logging Handlers", link: "/guides/logging-handlers" },
            {
              text: "Scheduler & Background Tasks",
              link: "/guides/scheduler",
            },
            { text: "Callbacks & Hooks", link: "/guides/callbacks" },
            {
              text: "Filter Features",
              link: "/guides/filter-features",
            },
            {
              text: "Source Location",
              link: "/guides/source-location",
            },
            {
              text: "Queue-Based Async",
              link: "/guides/queue-async",
            },
            {
              text: "Network Sink Config",
              link: "/guides/network-config",
            },
            {
              text: "Environment Variables",
              link: "/guides/environment-variables",
            },
          ],
        },
        {
          text: "Help",
          items: [
            { text: "Troubleshooting", link: "/guides/troubleshooting" },
            { text: "FAQ", link: "/guides/faq" },
            {
              text: "Switching from Other Libraries",
              link: "/guides/switching-from-other-libraries",
            },
          ],
        },
      ],
      "/integrations/": [
        {
          text: "Integrations",
          items: [{ text: "Overview", link: "/integrations/" }],
        },
        {
          text: "Frameworks & Libraries",
          items: [
            { text: "FastAPI", link: "/integrations/fastapi" },
            { text: "Django", link: "/integrations/django" },
            { text: "Flask", link: "/integrations/flask" },
            { text: "Starlette", link: "/integrations/starlette" },
            { text: "Stdlib", link: "/integrations/stdlib" },
            { text: "Gunicorn", link: "/integrations/gunicorn" },
            { text: "Uvicorn", link: "/integrations/uvicorn" },
            { text: "SQLAlchemy", link: "/integrations/sqlalchemy" },
            { text: "Structlog", link: "/integrations/structlog" },
            { text: "Rich", link: "/integrations/rich" },
            { text: "Click", link: "/integrations/click" },
            { text: "Typer", link: "/integrations/typer" },
            { text: "APScheduler", link: "/integrations/apscheduler" },
            { text: "RQ", link: "/integrations/rq" },
            { text: "Celery", link: "/integrations/celery" },
            { text: "Pydantic", link: "/integrations/pydantic" },
            { text: "tqdm", link: "/integrations/tqdm" },
            { text: "Propagate", link: "/integrations/propagate" },
          ],
        },
        {
          text: "Observability & Monitoring",
          items: [
            { text: "OpenTelemetry", link: "/integrations/opentelemetry" },
            { text: "Prometheus", link: "/integrations/prometheus" },
            { text: "Loki", link: "/integrations/loki" },
            { text: "Sentry", link: "/integrations/sentry" },
            { text: "Datadog", link: "/integrations/datadog" },
            { text: "New Relic", link: "/integrations/newrelic" },
            { text: "Seq", link: "/integrations/seq" },
            { text: "AWS CloudWatch", link: "/integrations/aws_cloudwatch" },
            {
              text: "Google Cloud Logging",
              link: "/integrations/google_cloud_logging",
            },
            { text: "Azure Monitor", link: "/integrations/azure_monitor" },
            { text: "Telemetry", link: "/integrations/telemetry" },
          ],
        },
        {
          text: "Data Stores & Message Brokers",
          items: [
            { text: "Elasticsearch", link: "/integrations/elasticsearch" },
            { text: "Redis", link: "/integrations/redis" },
            { text: "Kafka", link: "/integrations/kafka" },
            { text: "MongoDB", link: "/integrations/mongodb" },
            { text: "PostgreSQL", link: "/integrations/postgresql" },
            { text: "RabbitMQ", link: "/integrations/rabbitmq" },
            { text: "Logstash", link: "/integrations/logstash" },
            { text: "Graylog", link: "/integrations/graylog" },
          ],
        },
        {
          text: "Notifications & Webhooks",
          items: [
            { text: "Discord", link: "/integrations/discord" },
            { text: "Slack", link: "/integrations/slack" },
            { text: "Email", link: "/integrations/email" },
            { text: "HTTP", link: "/integrations/http" },
          ],
        },
      ],
      "/api-reference/": [
        {
          text: "API Reference",
          items: [
            { text: "Logger API", link: "/api-reference/logger" },
            { text: "Config Models", link: "/api-reference/models" },
            { text: "Exceptions", link: "/api-reference/exceptions" },
            { text: "Integrations", link: "/api-reference/integrations" },
          ],
        },
      ],
      "/examples/": [
        {
          text: "Examples",
          items: [
            { text: "Basic Logging", link: "/examples/basic-logging" },
            { text: "File Logging", link: "/examples/file-logging" },
            { text: "Multiple Sinks", link: "/examples/multiple-sinks" },
            { text: "JSON Logging", link: "/examples/json-logging" },
            { text: "Rotation", link: "/examples/rotation" },
            { text: "Compression", link: "/examples/compression" },
            { text: "Context Binding", link: "/examples/context-binding" },
            { text: "Custom Levels", link: "/examples/custom-levels" },
            {
              text: "Exception Handling",
              link: "/examples/exception-handling",
            },
            { text: "Filtering", link: "/examples/filtering" },
            { text: "Formatting", link: "/examples/formatting" },
            { text: "Concurrency", link: "/examples/concurrency" },
            { text: "Lazy Evaluation", link: "/examples/lazy-evaluation" },
            { text: "Patching", link: "/examples/patching" },
            { text: "Enable/Disable", link: "/examples/enable-disable" },
            { text: "Production Config", link: "/examples/production-config" },
            { text: "Integrations", link: "/examples/integrations" },
            {
              text: "Django Integration",
              link: "/examples/django-integration",
            },
            {
              text: "FastAPI Integration",
              link: "/examples/fastapi-integration",
            },
            { text: "Rich Integration", link: "/examples/rich-integration" },
            {
              text: "Stdlib Integration",
              link: "/examples/stdlib-integration",
            },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: "github", link: "https://github.com/muhammad-fiaz/logly" },
    ],

    footer: {
      message: "Released under the MIT License.",
      copyright: `Copyright © 2023-${new Date().getFullYear()} Muhammad Fiaz`,
    },

    search: {
      provider: "local",
    },

    editLink: {
      pattern: "https://github.com/muhammad-fiaz/logly/edit/main/docs/:path",
      text: "Edit this page on GitHub",
    },

    lastUpdated: {
      text: "Last updated",
      formatOptions: { dateStyle: "medium", timeStyle: "short" },
    },

    outline: [2, 3],
  },
});
