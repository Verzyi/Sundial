let current_path = window.location.pathname;
// console.log('Current Path:', current_path);
if (current_path.startsWith('/powder/search')) {
    button = document.getElementById('search')
    button.checked = true;
    // console.log('Button Check Value:', button.checked);
}
else if (current_path === '/powder/create/blend') {
    button = document.getElementById('create_blend')
    button.checked = true;
    // console.log('Button Check Value:', button.checked);
}
else if (current_path === '/powder/create/batch') {
    button = document.getElementById('create_batch')
    button.checked = true;
    // console.log('Button Check Value:', button.checked);
}
else if (current_path === '/powder/history/blend' || current_path === '/powder/history/batch') {
    button = document.getElementById('history')
    button.checked = true;
    // console.log('Button Check Value:', button.checked);
}
else if (current_path === '/powder/inventory/blend' || current_path === '/powder/inventory/batch') {
    button = document.getElementById('inventory')
    button.checked = true;
    // console.log('Button Check Value:', button.checked);
}
