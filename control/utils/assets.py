from flask_assets import Bundle


bundles = {
    'control_js': Bundle(
        'js/jquery-3.6.0.min.js',
        'js/jquery-ui.js',
        'js/main.js',
        output='gen/control.js'),

    'control_css': Bundle(
        'css/bootstrap.min.css',
        'css/bootstrap.min.css.map',
        'css/jquery-ui.css',
        'css/all.css',
        'css/main.css',
        output='gen/control.css'),
}
