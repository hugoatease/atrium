var React = require('react');
var request = require('superagent');
var ReactQuill = require('react-quill');
var moment = require('moment');
var DatePicker = require('react-datepicker');
var TimePicker = require('react-time-picker');
var clone = require('lodash/clone');
var browserHistory = require('react-router').browserHistory;
var moment = require('moment');
var humane = require('humane-js');

var EventCreate = React.createClass({
    getDefaultProps: function() {
        return {
            event_id: null
        }
    },

    getInitialState: function() {
        return {
            name: null,
            description: 'Enter description here',
            start_date: null,
            end_date: null,
            place: {
                name: null,
                address: null
            }
        }
    },

    componentDidMount: function() {
        if (this.props.event_id) {
            request.get('/api/events/' + this.props.event_id)
                .end(function(err, res) {
                    if (err) return;
                    this.setState({
                        name: res.body.name,
                        description: res.body.description,
                        start_date: moment(res.body.start_date),
                        end_date: moment(res.body.end_date),
                        place: {
                            name: res.body.place.name,
                            address: res.body.place.address
                        }
                    });

                    if (!this.state.description) {
                        this.setState({description: 'Enter description here'});
                    }
                }.bind(this));
        }
    },

    changedStartDate: function(date) {
        console.log(date);
        this.setState({
            start_date: date
        });
    },

    changedStartTime: function(datestring, date) {
        this.setState({
            start_date: date
        });
    },

    changedEndDate: function(date) {
        this.setState({
            end_date: date
        });
    },

    changedEndTime: function(datestring, date) {
        this.setState({
            end_date: date
        });
    },

    changedName: function(ev) {
        this.setState({
            name: ev.target.value
        });
    },

    changedDescription: function(text) {
        this.setState({description: text});
    },

    changedPlaceName: function(ev) {
        var place = clone(this.state.place);
        place.name = ev.target.value;
        this.setState({place: place});
    },

    changedPlaceAddress: function(ev) {
        var place = clone(this.state.place);
        place.address = ev.target.value;
        this.setState({place: place});
    },

    save: function(ev) {
        ev.preventDefault();
        if (!this.state.start_date || !this.state.end_date) {
            humane.log('<b>Error</b> You must specify event start and end dates');
            return;
        }

        var event_data = {
            name: this.state.name,
            club: this.props.club,
            description: this.state.description,
            start_date: this.state.start_date.toISOString(),
            end_date: this.state.end_date.toISOString(),
            place: {
                name: this.state.place.name,
                address: this.state.place.address
            }
        };

        if (!this.props.event_id) {
            request.post('/api/events')
                .send(event_data)
                .end(function(err, res) {
                    if (err) {
                        humane.log('Failed to create event');
                    }
                    else {
                        humane.log('Created event <b>' + res.body.id + '</b>');
                        browserHistory.push('/editor/events/' + res.body.id);
                    }
                });
        }
        else {
            request.put('/api/events/' + this.props.event_id)
                .send(event_data)
                .end(function(err, res) {
                    if (err) {
                        humane.log('Failed to update event');
                    }
                    else {
                        humane.log('Updated event <b>' + res.body.id + '</b>');
                    }
                });
        }
    },

    render: function() {
        var start_hour = null;
        if (this.state.start_date) {
            start_hour = (
                <div className="medium-6 columns">
                    <label>
                        <span>Start hour</span><br />
                        <TimePicker value={this.state.start_date} showArrows={false} format="HH mm" onChange={this.changedStartTime}/>
                    </label>
                </div>
            );
        }

        var end_hour = null;
        if (this.state.end_date) {
            end_hour = (
                <div className="medium-6 columns">
                    <label>
                        <span>End hour</span><br />
                        <TimePicker value={this.state.end_date} showArrows={false} format="HH mm" onChange={this.changedEndTime}/>
                    </label>
                </div>
            );
        }

        return (
            <form onSubmit={this.save}>
                <label>
                    <span>Event name</span>
                    <input type="text" placeholder="Event name" value={this.state.name} onChange={this.changedName} />
                </label>
                <label>
                    <span>Event description</span>
                    <ReactQuill placeholder="Event description" value={this.state.description} theme="snow" onChange={this.changedDescription} />
                </label>
                <div className="row">
                    <div className="medium-6 columns">
                        <label>
                            <span>Start date</span>
                            <DatePicker selected={this.state.start_date} onChange={this.changedStartDate} />
                        </label>
                    </div>
                    {start_hour}
                </div>
                <div className="row">
                    <div className="medium-6 columns">
                        <label>
                            <span>End date</span>
                            <DatePicker selected={this.state.end_date} onChange={this.changedEndDate} />
                        </label>
                    </div>
                    {end_hour}
                </div>
                <label>
                    <span>Place name</span>
                    <input type="text" placeholder="Place name" value={this.state.place.name} onChange={this.changedPlaceName} />
                </label>
                <label>
                    <span>Place address</span>
                    <input type="text" placeholder="Place address" value={this.state.place.address} onChange={this.changedPlaceAddress} />
                </label>
                <button type="submit" className="button success">Save event</button>
            </form>
        );
    }
});

module.exports = EventCreate;