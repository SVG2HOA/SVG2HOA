/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */
        
        './SVG2/templates/**/*.html',
        '../../SVG2/templates/**/*.html', // Adjust this to your actual template path
        '../../SVG2/static/js/**/*.js',
        '../../SVG2/static/css/**/*.js',
        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
          screens: {
            'xs': '480px',  // Custom breakpoint for very small screens
            'sm': '640px',  // Small devices (phones, 640px and up)
            'md': '768px',  // Medium devices (tablets, 768px and up)
            'lg': '1024px', // Large devices (laptops, 1024px and up)
            'xl': '1280px', // Extra large devices (large screens, 1280px and up)
            '2xl': '1536px', // 2x extra large devices (1536px and up)
            '3xl': '1920px', // 3x extra large devices (1920px and up)
          }
        }
      },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
