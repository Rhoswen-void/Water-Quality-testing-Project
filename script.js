const button = document.getElementById('generate-ph');
const display = document.getElementById('phValue');
button.addEventListener('click', () => {
    const phValue =Number((Math.random() * (13 - 0) + 1).toFixed(2));
    display.textContent = `pH Value: ${phValue}`;
});

