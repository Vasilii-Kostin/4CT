// menu.js — общее меню и подвал для всех страниц 4CT

document.addEventListener('DOMContentLoaded', function() {

    // --- Меню (верхняя навигация) ---
    const nav = document.createElement('nav');
    nav.style.cssText = `
        background: #2c3e50;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        display: flex;
        flex-wrap: wrap;
        gap: 1.2rem;
        align-items: center;
    `;
    nav.innerHTML = `
        <a href="index.html" style="color: white; text-decoration: none; font-weight: bold;">🏠 4CT</a>
        <a href="about.html" style="color: #ecf0f1; text-decoration: none;">О проекте</a>
        <a href="theory.html" style="color: #ecf0f1; text-decoration: none;">Теория</a>
        <a href="demo.html" style="color: #ecf0f1; text-decoration: none;">Демонстрация</a>
        <a href="contacts.html" style="color: #ecf0f1; text-decoration: none;">Контакты</a>
    `;

    // Вставляем меню в самое начало body
    document.body.prepend(nav);

    // --- Подвал (footer) ---
    const footer = document.createElement('footer');
    footer.style.cssText = `
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
        font-size: 0.9rem;
        color: #555;
        text-align: center;
    `;
    footer.innerHTML = `
        <p>Проект 4CT — конструктивное доказательство теоремы о четырёх красках и оптимизация раскраски.</p>
        <p>© 2026 Василий Костин</p>
    `;

    document.body.appendChild(footer);
});