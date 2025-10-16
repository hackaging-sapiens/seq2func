/**
 * Inline script that runs before React hydration to prevent view mode flicker
 * This sets a CSS class on the document root based on saved preference
 */
export function ViewModeScript() {
  return (
    <script
      dangerouslySetInnerHTML={{
        __html: `
          (function() {
            try {
              var savedView = localStorage.getItem('protein-view');
              if (savedView === 'table') {
                document.documentElement.setAttribute('data-view-mode', 'table');
              } else {
                document.documentElement.setAttribute('data-view-mode', 'grid');
              }
            } catch (e) {}
          })();
        `,
      }}
    />
  );
}
