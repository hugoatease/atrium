var React = require('react');
var request = require('superagent');
var Dropzone = require('react-dropzone');

var NewsMedia = React.createClass({
    getDefaultProps: function() {
        return {
            callback: null
        }
    },

    getInitialState: function() {
        return {
            medias: [],
            uploading: false
        }
    },

    componentDidMount: function() {
        request.get('/api/news/' + this.props.news_id)
            .end(function(err, res) {
                if (err) return;
                this.setState({medias: res.body.medias});
            }.bind(this));
    },

    uploadMedia: function(file) {
        this.setState({uploading: true});
        request.post('/api/news/' + this.props.news_id + '/medias')
            .attach('media', file[0])
            .end(function(err, res) {
                if (err) return;
                this.setState({uploading: false});
                this.setState({
                    medias: res.body.medias
                });
            }.bind(this));
    },

    select: function(media, ev) {
        ev.preventDefault();
        if (this.props.callback) {
            this.props.callback(media);
        }
    },

    render: function() {
        return (
            <div className="row medium-up-2">
                {this.state.medias.map(function(media) {
                    return (
                        <div className="column" onClick={this.select.bind(this, media)}>
                            <img src={media.url} className="thumbnail" />
                        </div>
                    );
                }.bind(this))}
                <div className="column">
                    <Dropzone multiple={false} onDrop={this.uploadMedia}>
                        {!this.state.uploading ? <span>
                            Drop your image or click to select file.
                        </span> : <span>Uploading image...</span>}
                    </Dropzone>
                </div>
            </div>
        );
    }
});

module.exports = NewsMedia;