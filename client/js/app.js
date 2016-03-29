var React = require('react');
var ReactDOM = require('react-dom');
var Router = require('react-router').Router;
var Route = require('react-router').Route;
var browserHistory = require('react-router').browserHistory;
var IndexRoute = require('react-router').IndexRoute;

var Editor = require('./Editor');
var ClubEdit = require('./ClubEdit');
var ProfileEdit = require('./ProfileEdit');
var ClubEvents = require('./ClubEvents');
var EventEdit = require('./EventEdit');
var ClubNews = require('./ClubNews');
var NewsEdit = require('./NewsEdit');
var ClubPermissions = require('./ClubPermissions');
var PermissionsEnroll = require('./PermissionsEnroll');
var FacebookEvents = require('./FacebookEvents');
var FacebookNews = require('./FacebookNews');

var App = React.createClass({
   render: function() {
       return (
           <div>
               {this.props.children}
           </div>
       )
   }
});

function renderEditor(container) {
    ReactDOM.render((
        <Router history={browserHistory}>
            <Route path="/editor" component={App}>
                <IndexRoute component={Editor} />
                <Route name="club-create" path="clubs/create" component={ClubEdit} />
                <Route name="club-edit" path="clubs/:slug" component={ClubEdit} />
                <Route name="profile-edit" path="profiles/:id" component={ProfileEdit} />
                <Route name="club-events" path="clubs/:slug/events" component={ClubEvents} />
                <Route name="club-facebook-events" path="clubs/:slug/events/facebook" component={FacebookEvents} />
                <Route name="club-facebook-events" path="clubs/:slug/news/facebook" component={FacebookNews} />
                <Route name="event-edit" path="events/:event_id" component={EventEdit} />
                <Route name="club-news" path="clubs/:slug/news" component={ClubNews} />
                <Route name="news-edit" path="news/:news_id" component={NewsEdit} />
                <Route name="club-permissions" path="clubs/:slug/permissions" component={ClubPermissions} />
                <Route name="permissions-enroll" path="permissions/enroll" component={PermissionsEnroll} />
            </Route>
        </Router>
    ), container);
}

module.exports = {
    renderEditor: renderEditor
}