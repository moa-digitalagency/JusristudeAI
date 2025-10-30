const PlatformSettings = {
    settings: {
        platform_name: 'LexIA',
        platform_tagline: 'Intelligence Artificielle au service du Droit',
        platform_description: 'Plateforme de recherche juridique alimentée par l\'IA',
        platform_keywords: 'jurisprudence, IA juridique, recherche juridique'
    },
    
    async load() {
        try {
            const response = await fetch('/api/settings');
            if (response.ok) {
                const data = await response.json();
                this.settings = { ...this.settings, ...data.settings };
                this.apply();
                return this.settings;
            }
        } catch (error) {
            console.log('Using default platform settings');
        }
        this.apply();
        return this.settings;
    },
    
    apply() {
        const platformNameElements = document.querySelectorAll('[data-platform-name]');
        platformNameElements.forEach(el => {
            el.textContent = this.settings.platform_name;
        });
        
        const platformTaglineElements = document.querySelectorAll('[data-platform-tagline]');
        platformTaglineElements.forEach(el => {
            el.textContent = this.settings.platform_tagline;
        });
        
        const titleElement = document.querySelector('title[data-dynamic]');
        if (titleElement) {
            const pageTitle = titleElement.getAttribute('data-page-title') || 'Page';
            titleElement.textContent = `${pageTitle} - ${this.settings.platform_name}`;
        }
        
        const metaDescription = document.querySelector('meta[name="description"]');
        if (metaDescription && this.settings.platform_description) {
            metaDescription.setAttribute('content', this.settings.platform_description);
        }
        
        const metaKeywords = document.querySelector('meta[name="keywords"]');
        if (metaKeywords && this.settings.platform_keywords) {
            metaKeywords.setAttribute('content', this.settings.platform_keywords);
        }
        
        const ogTitle = document.querySelector('meta[property="og:title"]');
        if (ogTitle) {
            ogTitle.setAttribute('content', `${this.settings.platform_name} - ${this.settings.platform_tagline}`);
        }
        
        const ogDescription = document.querySelector('meta[property="og:description"]');
        if (ogDescription && this.settings.platform_description) {
            ogDescription.setAttribute('content', this.settings.platform_description);
        }
    },
    
    get(key, defaultValue = '') {
        return this.settings[key] || defaultValue;
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PlatformSettings.load());
} else {
    PlatformSettings.load();
}
