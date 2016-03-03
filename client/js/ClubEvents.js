var React = require('react');
var request = require('superagent');

var EventList = require('./EventList');
var EventForm = require('./EventForm');

var ClubEvents  = React.createClass({
    render: function() {
        return (
            <div className="row">
                <div className="column medium-6">
                    <h5>Events for {this.props.params.slug}</h5><hr />
                    <EventList club={this.props.params.slug} />
                </div>
                <div className="column medium-6">
                    <h5>Create event</h5><hr />
                    <EventForm club={this.props.params.slug} />
                </div>
            </div>
        );
    }
});

module.exports = ClubEvents;