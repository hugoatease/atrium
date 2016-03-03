var React = require('react');
var request = require('superagent');

var EventList = React.createClass({
    getDefaultProps: function() {
        return {
            club: null
        }
    },

    getInitialState: function() {
        return {
            events: []
        }
    },

    componentDidMount: function() {
        var r = request.get('/api/events');
        if (this.props.club) {
            r = r.query({club: this.props.club});
        }
        r.end(function(err, res) {
            if (err) return;
            this.setState({
                events: res.body
            });
        }.bind(this));
    },

    render: function() {
        return (
            <div>
                {this.state.events.map(function(event) {
                    return (
                        <div className="callout">
                            <h5>{event.name}</h5>
                            <h6>{event.start_date} - {event.end_date}</h6>
                            <p dangerouslySetInnerHTML={{__html: event.description}}></p>
                        </div>
                    )
                }.bind(this))}
            </div>
        );
    }
});

module.exports = EventList;