var React = require('react');
var ReactDOM = require('react-dom');
var Router = require('react-router').Router;
var Route = require('react-router').Route;
var hashHistory = require('react-router').hashHistory;

var ClubEdit = require('./ClubEdit');

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
        <Router history={hashHistory}>
            <Route path="/" component={App}>
                <Route name="club-create" path="clubs" component={ClubEdit} />
                <Route name="club-edit" path="clubs/:slug" component={ClubEdit} />
            </Route>
        </Router>
    ), container);
}

module.exports = {
    renderEditor: renderEditor
}