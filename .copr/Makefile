srpm:                                                                                                                                                                                                                                       
	dnf -y install tito                                                                                                                                                                                                                 
	tito build --tgz --output=$(outdir)
	rpmbuild -bs -D '_sourcedir $(outdir)' -D '_srcrpmdir $(outdir)' '$(spec)'
