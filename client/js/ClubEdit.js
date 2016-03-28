var React = require('react');
var request = require('superagent');
var slug = require('slug');
var ReactQuill = require('react-quill');
var Dropzone = require('react-dropzone');
var MemberSearch = require('./MemberSearch');
var humane = require('humane-js');
var browserHistory = require('react-router').browserHistory;


var ClubEdit = React.createClass({
    getInitialState: function() {
        return {
            slug: this.props.params.slug,
            name: null,
            description: null,
            facebook_page: null,
            members: [],
            logo: null,
            uploading: false
        }
    },

    fetch: function(slug) {
        if (slug) {
            request.get('/api/clubs/' + slug)
                .end(function(err, res) {
                    if (err) return;
                    this.setState(res.body);
                }.bind(this));
        }
        else {
            this.setState({
                slug: null,
                name: null,
                description: null,
                facebook_page: null
            })
        }
    },

    componentDidMount: function() {
        this.fetch(this.props.params.slug);
    },

    componentWillReceiveProps: function(props) {
        this.fetch(props.params.slug);
    },

    handleNameChange: function(ev) {
        var name = ev.target.value;
        var state = {name: name};

        if (!this.props.params.slug) {
            state.slug = slug(name, {lower: true});
        }

        this.setState(state);
    },

    handleDescriptionChange: function(value) {
        this.setState({
            description: value
        });
    },

    handleFacebookChange: function(ev) {
        this.setState({facebook_page: ev.target.value});
    },

    save: function(ev) {
        ev.preventDefault();
        var data = {
            slug: this.state.slug,
            name: this.state.name,
            description: this.state.description,
            facebook_page: this.state.facebook_page
        };

        if (!this.props.params.slug) {
            request.post('/api/clubs')
                .send(data)
                .end(function(err, res) {
                    if (err) {
                        humane.log('Error creating club');
                    }
                    else {
                        humane.log('Created club <b>' + res.body.id + '</b>');
                        browserHistory.push('/editor/clubs/' + res.body.id);
                    }
                }.bind(this));;
        }
        else {
            request.put('/api/clubs/' + this.props.params.slug)
                .send(data)
                .end(function(err, res) {
                    if (err) {
                        humane.log('Error updating club');
                    }
                    else {
                        humane.log('Updated club <b>' + res.body.id + '</b>');
                    }
                }.bind(this));
        }
    },

    addMember: function(profile) {
        request.post('/api/clubs/' + this.state.slug + '/members')
            .send({'profile_id': profile.id})
            .end(function(err) {
                if (err) return;
                this.fetch(this.state.slug);
            }.bind(this));
    },

    removeMember: function(profile) {
        request.del('/api/clubs/' + this.state.slug + '/members')
            .send({profile_id: profile.id})
            .end(function(err) {
                if (err) return;
                this.fetch(this.state.slug);
            }.bind(this));
    },

    uploadPhoto: function(file) {
        this.setState({uploading: true});
        request.post('/api/clubs/' + this.state.slug + '/logo')
            .attach('logo', file[0])
            .end(function(err, res) {
                if (err) return;
                this.setState({uploading: false});
                this.setState(res.body);
            }.bind(this));
    },

    deletePhoto: function(ev) {
        ev.preventDefault();

        request.del('/api/clubs/' + this.state.slug + '/logo')
            .end(function(err, res) {
                if (err) return;
                this.fetch(this.state.slug);
            }.bind(this));
    },

    render: function() {
        var logo = null;
        if (this.props.params.slug) {
            if (!this.state.logo) {
                var logo = (
                    <Dropzone multiple={false} onDrop={this.uploadPhoto}>
                        {!this.state.uploading ? <span>
                            Drop your logo or click to select file.
                        </span> : <span>Uploading logo...</span>}
                    </Dropzone>
                );
            }
            else {
                var logo = (
                    <div>
                        <img src={this.state.logo} /><br />
                        <button className="button alert" onClick={this.deletePhoto}>Delete logo</button>
                    </div>
                )
            }
        }

        var members = null;
        if (this.props.params.slug) {
            members = (
                <div className="medium-6 column">
                    <h5>Club members</h5><hr />
                    <MemberSearch profiles={this.state.members} callback={this.removeMember} />

                    <h6>Add members</h6>
                    <p>Add club members by clicking on them</p>
                    <MemberSearch callback={this.addMember} />
                </div>
            );
        }

        return (
            <div className="row">
                <div className="medium-6 column">
                    <h5>Club information</h5><hr />
                    <form onSubmit={this.save}>
                        <label>
                            <span>Slug</span>
                            <input type="text" placeholder="Club slug" value={this.state.slug} disabled="true" />
                        </label>
                        <label>
                            <span>Name</span>
                            <input type="text" placeholder="Club name" value={this.state.name} onChange={this.handleNameChange} />
                        </label>
                        <label>
                            <span>Facebook Page ID</span>
                            <input type="text" placeholder="Club name" value={this.state.facebook_page} onChange={this.handleFacebookChange} />
                        </label>
                        {logo}
                        <label>
                            <span>Description</span>
                            <ReactQuill placeholder="Club description" value={this.state.description} theme="snow" onChange={this.handleDescriptionChange} />
                        </label>
                        <button type="submit" className="button success">Save</button>
                    </form>
                </div>
                {members}
            </div>
        )
    }
});

module.exports = ClubEdit;