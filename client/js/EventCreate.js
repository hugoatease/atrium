var React = require('react');
var request = require('superagent');
var ReactQuill = require('react-quill');
var moment = require('moment');
var DatePicker = require('react-datepicker');
var clone = require('lodash/clone');

var EventCreate = React.createClass({
    getInitialState: function() {
        return {
            name: null,
            description: null,
            start_date: null,
            end_date: null,
            place: {
                name: null,
                address: null
            }
        }
    },

    changedStartDate: function(date) {
        this.setState({
            start_date: date
        });
    },

    changedEndDate: function(date) {
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
        request.post('/api/events')
            .send({
                name: this.state.name,
                club: this.props.club,
                description: this.state.description,
                start_date: this.state.start_date.toISOString(),
                end_date: this.state.end_date.toISOString(),
                place: {
                    name: this.state.place.name,
                    address: this.state.place.address
                }
            })
            .end(function(err, res) {
                if (err) return;
                console.log('OK');
            })
    },

    render: function() {
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
                <label>
                    <span>Start date</span>
                    <DatePicker selected={this.state.start_date} onChange={this.changedStartDate} />
                </label>
                <label>
                    <span>End date</span>
                    <DatePicker selected={this.state.end_date} onChange={this.changedEndDate} />
                </label>
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