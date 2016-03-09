var gulp = require('gulp');
var sass = require('gulp-sass');
var minifyCss = require('gulp-minify-css');
var browserify = require('browserify');
var reactify = require('reactify');
var source = require('vinyl-source-stream');
var uglify = require('gulp-uglify');
var buffer = require('vinyl-buffer');

gulp.task('default', ['build']);
gulp.task('build', ['app', 'styles']);

gulp.task('app', function() {
   return browserify({
        entries: ['./client/js/app.js'],
        transform: [reactify],
        standalone: 'atrium',
   }).ignore('unicode/category/So')
    .bundle()
    .pipe(source('app.js'))
    .pipe(buffer())
    .pipe(uglify())
    .pipe(gulp.dest('atrium/static/'))
});

gulp.task('styles', function() {
   return gulp.src("styles.scss")
       .pipe(sass())
       .pipe(minifyCss())
       .pipe(gulp.dest('atrium/static/'));
});