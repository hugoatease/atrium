var React = require('react');
var EventForm = require('./EventForm');
var EventPoster = require('./EventPoster');
var request = require('superagent');
var browserHistory = require('react-router').browserHistory;
var humane = require('humane-js');
var Link = require('react-router').Link;

var EventEdit = React.createClass({
    remove: function() {
        request.del('/api/events/' + this.props.params.event_id)
            .end(function(err, res) {
                if (err) return;
                browserHistory.goBack();
            }.bind(this));
    },

    render: function() {
        return (
            <div className="row">
                <div className="medium-6 column">
                    <div className="clearfix">
                        <h5 className="float-left">Event details</h5>
                        <Link className="button primary float-right" to={'/editor/events/' + this.props.params.event_id + '/facebook_publish'}>
                            Publish to Facebook
                        </Link>
                    </div>
                    <EventForm event_id={this.props.params.event_id} />
                    <button onClick={this.remove} className="button alert">Delete event</button>
                </div>
                <div className="medium-6 column">
                    <h5>Event poster</h5><hr />
                    <EventPoster event_id={this.props.params.event_id} />
                </div>
            </div>
        );
    }
});

module.exports = EventEdit;