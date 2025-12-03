(function () {
    let config = {};
    let menuOpen = false;

    // Create overlay for background click
    const overlay = document.createElement('div');
    overlay.style.cssText = "position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: none;";
    document.body.appendChild(overlay);

    const menu = document.createElement('div');
    menu.style.cssText = "position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0, 0, 0, 0.9); color: white; padding: 20px; border-radius: 10px; font-family: sans-serif; z-index: 10000; display: none; max-height: 80vh; overflow-y: auto; min-width: 300px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid #444;";
    document.body.appendChild(menu);

    // Close function
    function closeMenu() {
        menuOpen = false;
        menu.style.display = 'none';
        overlay.style.display = 'none';
    }

    // Open function
    function openMenu() {
        menuOpen = true;
        menu.style.display = 'block';
        overlay.style.display = 'block';
    }

    // Toggle function
    function toggleMenu() {
        if (menuOpen) closeMenu();
        else openMenu();
    }

    // Background click close
    overlay.addEventListener('click', closeMenu);

    // Fetch config
    fetch('config.json')
        .then(res => res.json())
        .then(data => {
            config = data;
            if (config.options) {
                buildMenu(config.options);
                // Run onload callbacks
                Object.values(config.options).forEach(opt => {
                    if (opt.onchangeload) {
                        try {
                            const fn = eval(opt.onchangeload);
                            if (typeof fn === 'function') fn(opt.value);
                        } catch (e) { console.error(e); }
                    }
                });
            }
        })
        .catch(err => console.error("Error loading config:", err));

    document.body.addEventListener('dblclick', toggleMenu);

    function buildMenu(options) {
        // Header container
        const header = document.createElement('div');
        header.style.cssText = "display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #555; padding-bottom: 10px;";

        const title = document.createElement('h3');
        title.innerText = "Options";
        title.style.margin = "0";

        const closeBtn = document.createElement('button');
        closeBtn.innerText = "X"; // Safe character
        closeBtn.style.cssText = "background: none; border: none; color: #aaa; font-size: 16px; font-weight: bold; cursor: pointer; padding: 5px 10px;";
        closeBtn.onmouseover = () => closeBtn.style.color = "white";
        closeBtn.onmouseout = () => closeBtn.style.color = "#aaa";
        closeBtn.onclick = closeMenu;

        header.appendChild(title);
        header.appendChild(closeBtn);
        menu.appendChild(header);

        for (const [key, opt] of Object.entries(options)) {
            const row = document.createElement('div');
            row.style.marginBottom = '15px';

            const label = document.createElement('label');
            label.textContent = opt.label || key;
            label.style.display = 'block';
            label.style.marginBottom = '5px';
            label.style.fontSize = '14px';
            label.style.color = '#ddd';
            row.appendChild(label);

            // Infer type if missing
            let type = opt.type;
            if (!type) {
                if (typeof opt.value === 'boolean') type = 'checkbox';
                else if (typeof opt.value === 'number') type = 'range';
                else if (Array.isArray(opt.options)) type = 'select';
                else if (typeof opt.value === 'string' && opt.value.startsWith('#')) type = 'color-picker';
                else type = 'text';
            }

            let input;
            if (type === 'select') {
                input = document.createElement('select');
                input.style.padding = '5px';
                input.style.borderRadius = '4px';
                input.style.border = '1px solid #555';
                input.style.background = '#333';
                input.style.color = 'white';
                input.style.width = '100%';
                if (opt.options) {
                    opt.options.forEach(val => {
                        const option = document.createElement('option');
                        option.value = val;
                        option.textContent = val;
                        if (val === opt.value) option.selected = true;
                        input.appendChild(option);
                    });
                }
            } else if (type === 'checkbox') {
                input = document.createElement('input');
                input.type = 'checkbox';
                input.checked = opt.value;
                input.style.transform = "scale(1.2)";
                input.style.cursor = "pointer";
            } else if (type === 'color-picker') {
                input = document.createElement('input');
                input.type = 'color';
                input.value = opt.value;
                input.style.border = 'none';
                input.style.width = '100%';
                input.style.height = '30px';
                input.style.cursor = 'pointer';
                input.style.background = 'none';
            } else if (type === 'range') {
                input = document.createElement('input');
                input.type = 'range';
                input.min = opt.min !== undefined ? opt.min : 0;
                input.max = opt.max !== undefined ? opt.max : 100;
                input.step = opt.step !== undefined ? opt.step : 1;
                input.value = opt.value;
                input.style.width = '100%';
                input.style.cursor = "pointer";
            } else {
                // Fallback text input
                input = document.createElement('input');
                input.type = 'text';
                input.value = opt.value;
                input.style.width = '100%';
                input.style.padding = '5px';
                input.style.background = '#333';
                input.style.border = '1px solid #555';
                input.style.color = 'white';
            }

            if (input) {
                input.addEventListener('input', (e) => {
                    const val = input.type === 'checkbox' ? input.checked : input.value;
                    if (opt.onchangeload) {
                        try {
                            let fn = eval(opt.onchangeload);
                            if (typeof fn === 'function') fn(val);
                        } catch (err) { console.error(err); }
                    }
                });
                row.appendChild(input);
            }
            menu.appendChild(row);
        }
    }
})();
