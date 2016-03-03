var React = require('react');
var ReactDOM = require('react-dom');
var Router = require('react-router').Router;
var Route = require('react-router').Route;
var browserHistory = require('react-router').browserHistory;

var ClubEdit = require('./ClubEdit');
var ProfileEdit = require('./ProfileEdit');

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
                <Route name="club-create" path="clubs/create" component={ClubEdit} />
                <Route name="club-edit" path="clubs/:slug" component={ClubEdit} />
                <Route name="profile-edit" path="profiles/:id" component={ProfileEdit} />
            </Route>
        </Router>
    ), container);
}

module.exports = {
    renderEditor: renderEditor
}