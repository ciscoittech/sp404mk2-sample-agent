
import { createContext, useState, useEffect } from 'react';

import React from "react";
import useSWR from 'swr';
import { getFetcher, postFetcher } from 'src/api/globalFetcher';


// Create context
export const UserDataContext = createContext(undefined);

// Default config values
const config = {
    posts: [],
    users: [],
    gallery: [],
    followers: [],
    search: '',
    loading: true,
};

export const UserDataProvider = ({ children }) => {
    const [posts, setPosts] = useState(config.posts);
    const [users, setUsers] = useState(config.users);
    const [gallery, setGallery] = useState(config.gallery);
    const [followers, setFollowers] = useState(config.followers);
    const [search, setSearch] = useState(config.search);
    const [loading, setLoading] = useState(config.loading);
    const [error, setError] = useState(config.error);
    const [profileData] = useState({
        name: 'Mathew Anderson',
        role: 'Designer',
        avatar: '/images/profile/user-1.jpg',
        coverImage: '/images/backgrounds/profilebg.jpg',
        postsCount: 938,
        followersCount: 3586,
        followingCount: 2659,
    });

    const { data: postsData, isLoading: isPostsLoading, error: postsError, mutate } = useSWR("/api/data/postData", getFetcher);
    const { data: usersData, isLoading: isUsersLoading, error: usersError } = useSWR("/api/data/users", getFetcher);
    const { data: galleryData, isLoading: isGalleryLoading, error: galleryError } = useSWR("/api/data/gallery", getFetcher);

    useEffect(() => {
        if (postsData && usersData && galleryData) {
            setPosts(postsData.data);
            setLoading(isPostsLoading)
            setUsers(usersData.data);
            setLoading(isUsersLoading);
            setFollowers(usersData.data);
            setGallery(galleryData.data);
            setLoading(isGalleryLoading);
        }
        else if (postsError) {
            setError(postsError);
            setLoading(isPostsLoading)
        } else if (usersError) {
            setError(usersError);
            setLoading(isUsersLoading)
        } else if (galleryError) {
            setError(galleryError);
            setLoading(isGalleryLoading)
        } else {
            setLoading(isGalleryLoading);
        }

    }, [postsData, usersData, galleryData, isPostsLoading, isUsersLoading, isGalleryLoading, galleryError, postsError, usersError]);


    // Function to add a new item to the gallery
    const addGalleryItem = (item) => {
        setGallery((prevGallery) => [...prevGallery, item]);
    };

    // Function to toggle follow/unfollow status of a user
    const toggleFollow = (id) => {
        setFollowers((prevFollowers) =>
            prevFollowers.map((follower) =>
                follower.id === id ? { ...follower, isFollowed: !follower.isFollowed } : follower
            )
        );
    };

    // Function to filter followers based on search input
    const filterFollowers = () => {
        if (followers) {
            return followers.filter((t) =>
                t.name.toLowerCase().includes(search.toLowerCase())
            );
        }
        return followers;
    };

    // Add comment to a post
    const addComment = async (postId, comment) => {
        try {
            await mutate(postFetcher('/api/data/posts/comments/add', {
                postId,
                comment,
            }))
        } catch (error) {
            console.error('Error adding comment:', error);
        }
    };

    // Add reply to a comment
    const addReply = async (postId, commentId, reply) => {
        try {
            await mutate(postFetcher('/api/data/posts/replies/add', {
                postId,
                commentId,
                reply,
            }))
        } catch (error) {
            console.error('Error adding reply:', error);
        }
    };

    // Function to toggle like/unlike a post
    const likePost = async (postId) => {
        try {
            await mutate(postFetcher('/api/data/posts/like', { postId }))
        } catch (error) {
            console.error('Error liking post:', error);
        }
    };

    // Function to toggle like/unlike a reply to a comment
    const likeReply = async (postId, commentId) => {
        try {
            await mutate(postFetcher('/api/data/posts/replies/like', { postId, commentId }))
        } catch (error) {
            console.error('Error liking reply:', error);
        }
    };

    return (
        <UserDataContext.Provider value={{
            posts,
            users,
            error,
            gallery,
            loading,
            profileData,
            addGalleryItem,
            addReply,
            likePost,
            addComment,
            likeReply,
            followers: filterFollowers(),
            toggleFollow,
            setSearch,
            search
        }}>
            {children}
        </UserDataContext.Provider>
    );
};