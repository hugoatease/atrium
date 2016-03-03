var React = require('react');
var request = require('superagent');
var Dropzone = require('react-dropzone');

var EventPoster = React.createClass({
    getInitialState: function() {
       return {
           poster: null,
           uploading: false
       }
    },

    componentDidMount: function() {
        request.get('/api/events/' + this.props.event_id)
            .end(function(err, res) {
                if (err) return;
                this.setState({
                    poster: res.body.poster
                })
            }.bind(this));
    },

    uploadPoster: function(file) {
        this.setState({uploading: true});
        request.post('/api/events/' + this.props.event_id + '/poster')
            .attach('poster', file[0])
            .end(function(err, res) {
                if (err) return;
                this.setState({uploading: false});
                this.setState({
                    poster: res.body.poster
                });
            }.bind(this));
    },

    render: function() {
        if (!this.state.poster) {
            var poster = (
                <Dropzone multiple={false} onDrop={this.uploadPoster}>
                    {!this.state.uploading ? <span>
                        Drop your poster or click to select file.
                    </span> : <span>Uploading poster...</span>}
                </Dropzone>
            );
        }
        else {
            var poster = (
                <div>
                    <img src={this.state.poster} width="300" />
                </div>
            )
        }

        return (
            <div>
                {poster}
            </div>
        );
    }
});

module.exports = EventPoster;