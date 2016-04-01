var React = require('react');
var EventForm = require('./EventForm');
var EventPoster = require('./EventPoster');
var request = require('superagent');
var browserHistory = require('react-router').browserHistory;
var humane = require('humane-js');

var EventEdit = React.createClass({
    facebookPublish: function() {
        humane.log('Publishing event on Facebook...')
        request.post('/api/events/' + this.props.params.event_id + '/facebook_publish')
            .end(function(err, res) {
                if (err) {
                    humane.log('Failed to publish event on Facebook');
                }
                else {
                    humane.log('Event published on Facebook');
                }
            });
    },

    remove: function() {
        request.del('/api/events/' + this.props.params.event_id)
            .end(function(err, res) {
                if (err) return;
                browserHistory.goBack();
            }.bind(this));
    },

    render: function() {
        console.log(this.props);
        return (
            <div className="row">
                <div className="medium-6 column">
                    <div className="clearfix">
                        <h5 className="float-left">Event details</h5>
                        <button className="button primary float-right" onClick={this.facebookPublish}>Publish to Facebook</button>
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