var React = require('react');
var EventForm = require('./EventForm');

var EventEdit = React.createClass({
    render: function() {
        return (
            <div className="row">
                <div className="medium-6">
                    <EventForm event_id={this.props.params.event_id} />
                </div>
            </div>
        );
    }
});

module.exports = EventEdit;