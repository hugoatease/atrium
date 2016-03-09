var React = require('react');
var request = require('superagent');
var moment = require('moment');
var ReactQuill = require('react-quill');
var browserHistory = require('react-router').browserHistory;
var humane = require('humane-js');

var NewsForm = React.createClass({
    getDefaultProps: function() {
        return {
            news_id: null
        }
    },

    getInitialState: function() {
        return {
            name: null,
            headline: null,
            content: null,
            club: null
        }
    },

    componentDidMount: function() {
        if (this.props.news_id) {
            request.get('/api/news/' + this.props.news_id)
                .end(function(err, res) {
                    if (err) return;
                    this.setState(res.body);
                }.bind(this));
        }
    },

    save: function(ev) {
        ev.preventDefault();
        var news_data = {
            name: this.state.name,
            club: this.props.club,
            headline: this.state.headline,
            content: this.state.content
        };

        if (!this.props.news_id) {
            request.post('/api/news')
                .send(news_data)
                .end(function(err, res) {
                    if (err) {
                        humane.log('Failed to create news');
                    }
                    else {
                        humane.log('Created news <b>' + res.body.id + '</b>');
                        browserHistory.push('/editor/news/' + res.body.id);
                    }
                }.bind(this));
        }
        else {
            request.put('/api/news/' + this.props.news_id)
                .send(news_data)
                .end(function(err, res) {
                    if (err) {
                        humane.log('Failed to update news')
                    }
                    else {
                        humane.log('Updated news <b>' + res.body.id + '</b>');
                    }
                }.bind(this));
        }
    },

    remove: function(ev) {
        ev.preventDefault();
        
        request.del('/api/news/' + this.props.news_id)
            .end(function(err) {
                if (err) {
                    humane.log('<b>Error</b> Failed to delete news');
                }
                else {
                    humane.log('Deleted news ' + this.props.news_id);
                    browserHistory.push('/editor/clubs/' + this.state.club.id + '/news');
                }
            }.bind(this));
    },

    onNameChange: function(ev) {
        this.setState({
            name: ev.target.value
        });
    },

    onHeadlineChange: function(ev) {
        this.setState({
            headline: ev.target.value
        })
    },

    onContentChange: function(text) {
        this.setState({
            content: text
        });
    },

    render: function() {
        var del = null;
        if (this.props.news_id) {
            del = <button className="button alert" onClick={this.remove}>Delete news</button>;
        }

        return (
            <form onSubmit={this.save}>
                <label>
                    <span>News title</span>
                    <input type="text" placeholder="News title" value={this.state.name} onChange={this.onNameChange} />
                </label>
                <label>
                    <span>Healine</span>
                    <input type="text" placeholder="Headline" value={this.state.headline} onChange={this.onHeadlineChange} />
                </label>
                <label>
                    <span>News content</span>
                    <ReactQuill placeholder="News content" value={this.state.content} theme="snow" onChange={this.onContentChange} />
                </label>
                <button type="submit" className="button success">Save news</button>
                &nbsp;&nbsp;
                {del}
            </form>
        );
    }
});

module.exports = NewsForm;