var React = require('react');
var EventForm = require('./EventForm');
var EventPoster = require('./EventPoster');

var EventEdit = React.createClass({
    render: function() {
        return (
            <div className="row">
                <div className="medium-6 column">
                    <h5>Event details</h5><hr />
                    <EventForm event_id={this.props.params.event_id} />
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