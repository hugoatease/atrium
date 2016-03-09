var React = require('react');
var request = require('superagent');
var moment = require('moment');
var ReactQuill = require('react-quill');
var browserHistory = require('react-router').browserHistory;

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
            content: null
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
                    if (err) return;
                    browserHistory.push('/editor/news/' + res.body.id);
                }.bind(this));
        }
        else {
            request.put('/api/news/' + this.props.news_id)
                .send(news_data)
                .end(function(err, res) {
                    if (err) return;
                }.bind(this));
        }
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
            </form>
        );
    }
});

module.exports = NewsForm;